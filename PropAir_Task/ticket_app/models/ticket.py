from django.db import models
from django.contrib.auth.models import User
from ticket_app.models.event import Event

class Ticket(models.Model):
    class Meta:
        verbose_name_plural = "Ticket"
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.event} - {self.user}'
