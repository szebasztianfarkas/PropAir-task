from django.db import models
from ticket_app.models.ticket import Ticket
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Order(models.Model):
    class Meta:
        verbose_name_plural = "Order"

    class OrderStatus(models.TextChoices):
        PENDING = "PEND", _("Pending")
        COMPLETED = "COMP", _("Completed")
        FAILED = "FAIL", _("Failed")
    
    tickets = models.ManyToManyField(Ticket)
    status = models.CharField(max_length=4, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.id} - {self.get_status_display()}"
