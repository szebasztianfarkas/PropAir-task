from datetime import timedelta
from django.utils import timezone
from ticket_app.models.order import Order

def expire_overdue_orders(ttl: timedelta) -> int:
    cutoff = timezone.now() - ttl
    return (Order.objects
            .filter(status=Order.OrderStatus.PENDING, created_at__lt=cutoff)
            .update(status=Order.OrderStatus.FAILED))