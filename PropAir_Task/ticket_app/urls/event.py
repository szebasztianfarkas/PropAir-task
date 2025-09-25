from django.urls import path
from ticket_app.views.event import EventListCreate, EventModify

urlpatterns = [
    path("", EventListCreate.as_view()),
    path("<int:pk>/", EventModify.as_view()),
]