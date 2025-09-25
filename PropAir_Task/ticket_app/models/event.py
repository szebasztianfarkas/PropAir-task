from django.db import models
from django.utils import timezone

class Event(models.Model):
    class Meta:
        verbose_name_plural = "Event"
    
    description = models.CharField(max_length=255)
    date = models.DateField(default=timezone.now)
    location = models.CharField(max_length=255)
    max_amount = models.BigIntegerField(default=1)

    def __str__(self):
        return f'{self.location} - {self.date}'
