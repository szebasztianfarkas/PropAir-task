from django.contrib import admin
from ticket_app.models.event import Event
from ticket_app.models.order import Order
from ticket_app.models.ticket import Ticket

admin.site.register(Event)
admin.site.register(Order)
admin.site.register(Ticket)