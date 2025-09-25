from django.urls import path
from ticket_app.views.order import OrderListCreate, OrderModify, OrderFakePayment

urlpatterns = [
    path("", OrderListCreate.as_view()),
    path("<int:pk>/", OrderModify.as_view()),
    path("pay/<int:pk>/", OrderFakePayment.as_view()),
]