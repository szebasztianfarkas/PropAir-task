from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.shortcuts import render

from django.contrib.auth import get_user_model
from ticket_app.models.event import Event
from ticket_app.models.ticket import Ticket
from ticket_app.models.order import Order

User = get_user_model()

@staff_member_required
def stats(request):
    per_event = (
        Event.objects
        .annotate(
            sold=Count("ticket", filter=Q(ticket__order__status=Order.OrderStatus.COMPLETED), distinct=True)
        )
        .values("id", "description", "date", "location", "max_amount", "sold")
        .order_by("date", "id")
    )

    paid_tickets = (
        Ticket.objects.filter(order__status=Order.OrderStatus.COMPLETED)
        .distinct()
        .count()
    )
    expired_tickets = (
        Ticket.objects.filter(order__status=Order.OrderStatus.FAILED)
        .distinct()
        .count()
    )

    top_users_qs = (
        User.objects
        .annotate(paid_count=Count("ticket", filter=Q(ticket__order__status=Order.OrderStatus.COMPLETED), distinct=True))
        .order_by("-paid_count", "id")[:5]
    )
    top_users = [
        {"id": u.id, "username": getattr(u, 'username', None), "paid_count": u.paid_count}
        for u in top_users_qs
    ]

    ctx = {
        "per_event": list(per_event),
        "paid_tickets": paid_tickets,
        "expired_tickets": expired_tickets,
        "top_users": top_users,
    }
    return render(request, "admin/stats.html", ctx)