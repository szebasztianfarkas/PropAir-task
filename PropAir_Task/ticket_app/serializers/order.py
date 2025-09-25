from rest_framework import serializers
from ticket_app.models.order import Order
from ticket_app.models.event import Event
from ticket_app.services.ticket import create_ticket_service

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ['created_at']

class OrderCreateSerializer(serializers.Serializer):
    ticket_amount = serializers.IntegerField()
    event_id = serializers.IntegerField()

    def validate_event_id(self, value):
        if not Event.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Event not found.")
        return value
    
    def validate_ticket_amount(self, value: int):
        if value <= 0:
            raise serializers.ValidationError("ticket_amount must be positive.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        event_id = validated_data["event_id"]
        qty = validated_data["ticket_amount"]

        tickets, terr = create_ticket_service({"event": event_id, "quantity": qty}, acting_user=user)
        if terr:
            raise serializers.ValidationError(terr)

        order = Order.objects.create()
        order.tickets.add(*tickets)

        return order