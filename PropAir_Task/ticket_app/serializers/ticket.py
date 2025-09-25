from rest_framework import serializers
from ticket_app.models.ticket import Ticket

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"