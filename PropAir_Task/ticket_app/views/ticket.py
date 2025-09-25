from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ticket_app.models.ticket import Ticket
from ticket_app.serializers.ticket import TicketSerializer
from django.shortcuts import get_object_or_404
from ticket_app.services.ticket import (
    create_ticket_service,
    update_ticket_service,
    delete_ticket_service,
)

class TicketCreate(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        ticket, errors = create_ticket_service(request.data, acting_user=request.user)
        if errors:
            http_status = 400
            if isinstance(errors, dict) and errors.get("detail") == "Forbidden":
                http_status = status.HTTP_403_FORBIDDEN
            return Response(errors, status=http_status)

        return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)


class TicketModify(APIView):
    permission_classes = [permissions.IsAdminUser]

    def put(self, request, pk):
        ticket = get_object_or_404(Ticket, id=pk)
        updated, errors, http_status = update_ticket_service(ticket, request.data, partial=False, acting_user=request.user)
        if errors:
            return Response(errors, status=http_status or status.HTTP_400_BAD_REQUEST)
        return Response(TicketSerializer(updated).data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        ticket = get_object_or_404(Ticket, id=pk)
        updated, errors, http_status = update_ticket_service(ticket, request.data, partial=True, acting_user=request.user)
        if errors:
            return Response(errors, status=http_status or status.HTTP_400_BAD_REQUEST)
        return Response(TicketSerializer(updated).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        ticket = get_object_or_404(Ticket, id=pk)
        err = delete_ticket_service(ticket, acting_user=request.user)
        if err:
            return Response(err, status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_204_NO_CONTENT)