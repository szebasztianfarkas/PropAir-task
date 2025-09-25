from typing import Tuple, Optional, Dict, Any
from django.contrib.auth import get_user_model
from ticket_app.models.ticket import Ticket
from ticket_app.serializers.ticket import TicketSerializer
from ticket_app.utils.permissions import is_admin
from ticket_app.models.event import Event
from ticket_app.models.order import Order

User = get_user_model()

def _force_owner_field(payload: Dict[str, Any], user) -> Dict[str, Any]:
    payload = dict(payload)
    payload['user'] = getattr(user, "pk", user)
    return payload


USER_PER_EVENT_LIMIT = 5

def _extra_user_checks_or_error(payload: Dict[str, Any], user) -> Optional[Dict[str, str]]:
    event = payload.get("event")
    if isinstance(event, int):
        try:
            event = Event.objects.get(pk=event)
        except Event.DoesNotExist:
            return {"detail": "Event not found.", "event_id": payload.get("event")}
    elif not isinstance(event, Event):
        return {"detail": "Missing or invalid 'event' in payload."}

    try:
        quantity = int(payload.get("quantity", 1) or 1)
    except (TypeError, ValueError):
        return {"detail": "'quantity' must be an integer."}

    if quantity <= 0:
        return {"detail": "'quantity' must be a positive integer."}

    active_statuses = [Order.OrderStatus.PENDING, Order.OrderStatus.COMPLETED]

    user_has = (
    Ticket.objects
        .filter(event=event, user=user, order__status__in=active_statuses)
        .distinct()
        .count()
    )
    user_left = max(USER_PER_EVENT_LIMIT - user_has, 0)
    if quantity > user_left:
        return {
            "detail": "User ticket limit reached for this event.",
            "requested": quantity,
            "user_limit": USER_PER_EVENT_LIMIT,
            "user_left_for_event": user_left,
            "event_id": event.id,
        }

    issued = (
    Ticket.objects
        .filter(event=event, order__status__in=active_statuses)
        .distinct()
        .count()
    )
    capacity_left = max(event.max_amount - issued, 0)
    if quantity > capacity_left:
        return {
            "detail": "Not enough capacity for this event.",
            "requested": quantity,
            "capacity_left": capacity_left,
            "event_id": event.id,
            "max_amount": event.max_amount,
        }
    return None


def create_ticket_service(data: Dict[str, Any], *, acting_user) -> Tuple[Optional[Ticket], Optional[Dict[str, Any]]]:
    payload = data
    qty = payload.get('quantity')

    payload = _force_owner_field(payload, acting_user)

    err = None
    if not is_admin(acting_user):
        err = _extra_user_checks_or_error(payload, acting_user)
    if err:
        return None, err

    tickets = []
    for _ in range(qty):
        serializer = TicketSerializer(data=payload)
        if serializer.is_valid():
            ticket = serializer.save()
            tickets.append(ticket)
        else:
            return None, serializer.errors
    return tickets, None


def update_ticket_service(ticket: Ticket, data: Dict[str, Any], *, partial: bool, acting_user) -> Tuple[Optional[Ticket], Optional[Dict[str, Any]], Optional[int]]:
    if not is_admin(acting_user):
        return None, {"detail": "Forbidden"}, 403
    
    if data.get('user'):
        return None, "User cannot be set after ticket creation", 400

    serializer = TicketSerializer(instance=ticket, data=data, partial=partial)
    if serializer.is_valid():
        return serializer.save(), None, None
    return None, serializer.errors, 400


def delete_ticket_service(ticket: Ticket, *, acting_user) -> Optional[Dict[str, Any]]:
    if not is_admin(acting_user):
        return {"detail": "Forbidden"}
    ticket.delete()
    return None