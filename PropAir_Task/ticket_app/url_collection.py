from django.urls import path, include

urlpatterns = [
    path('event/', include('ticket_app.urls.event')),
    path('order/', include('ticket_app.urls.order')),
    path('ticket/', include('ticket_app.urls.ticket')),
    path('admin/', include('ticket_app.urls.admin')),
]
