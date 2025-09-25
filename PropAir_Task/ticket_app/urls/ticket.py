from django.urls import path
from ticket_app.views.ticket import TicketCreate, TicketModify

urlpatterns = [
    path("", TicketCreate.as_view()),
    path("<int:pk>/", TicketModify.as_view()),
]