from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from ticket_app.models.order import Order
from ticket_app.models.ticket import Ticket


def is_admin(user) -> bool:
    return bool(user and (user.is_staff or user.is_superuser))


def can_access_order(user, order) -> bool:
    if is_admin(user):
        return True
    return order.tickets.filter(user=user).exists()


def filter_orders_for_user(qs, user):
    if is_admin(user):
        return qs
    return qs.filter(tickets__user=user).distinct()


def get_order_or_404_for_user(pk, user, base_qs=None):
    qs = base_qs or Order.objects.all()
    qs = filter_orders_for_user(qs, user)
    return get_object_or_404(qs, id=pk)


def require_order_access(user, order):
    if not can_access_order(user, order):
        raise PermissionDenied("Forbidden")


def user_owns_all_ticket_ids(user, ticket_ids) -> bool:
    if is_admin(user):
        return True
    return not Ticket.objects.filter(id__in=ticket_ids).exclude(user=user).exists()