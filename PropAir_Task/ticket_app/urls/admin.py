from django.urls import path
from ticket_app.views.admin import stats

urlpatterns = [
    path("stats/", stats, name="admin-stats"),
]