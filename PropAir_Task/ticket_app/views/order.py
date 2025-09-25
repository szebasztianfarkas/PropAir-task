from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ticket_app.models.order import Order
from ticket_app.serializers.order import OrderSerializer, OrderCreateSerializer
from django.shortcuts import get_object_or_404
from ticket_app.utils.permissions import filter_orders_for_user
import random


class OrderListCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = filter_orders_for_user(
            Order.objects.prefetch_related('tickets'),
            request.user
        )
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class OrderModify(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [permissions.IsAdminUser()]
        if self.request.method == "DELETE":
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def put(self, request, pk):
        order = get_object_or_404(Order, id=pk)
        serializer = OrderSerializer(instance=order, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        order = get_object_or_404(Order, id=pk)
        serializer = OrderSerializer(instance=order, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        order = get_object_or_404(Order, id=pk)

        if not (request.user.is_staff or order.tickets.filter(user=request.user).exists()):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        order.tickets.all().delete()
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class OrderFakePayment(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        order = get_object_or_404(Order, id=pk)

        if order.status != Order.OrderStatus.PENDING:
            return Response({"detail": "Only pending orders can be updated."}, status=status.HTTP_400_BAD_REQUEST)

        new_status = (
            Order.OrderStatus.COMPLETED
            if random.getrandbits(1)
            else Order.OrderStatus.FAILED
        )

        serializer = OrderSerializer(instance=order, data={"status": new_status}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)