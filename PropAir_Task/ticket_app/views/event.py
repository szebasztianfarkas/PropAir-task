from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ticket_app.models.event import Event
from ticket_app.serializers.event import EventSerializer
from django.shortcuts import get_object_or_404


class EventListCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def get(self, request):
        Events = Event.objects.all()
        serializer = EventSerializer(Events, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class EventModify(APIView):
    permission_classes = [permissions.IsAdminUser]

    def put(self, request, pk):
        event = get_object_or_404(Event, id=pk)
        serializer = EventSerializer(instance=event, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        event = get_object_or_404(Event, id=pk)
        serializer = EventSerializer(instance=event, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        event = get_object_or_404(Event, id=pk)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)