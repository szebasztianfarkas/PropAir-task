from datetime import timedelta
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from apscheduler.schedulers.background import BackgroundScheduler
from ticket_app.services.order import expire_overdue_orders

scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
scheduler.add_jobstore(DjangoJobStore(), "default")

@register_job(
    scheduler,
    "interval",
    minutes=5,
    id="expire_orders_job",
    replace_existing=True,
    max_instances=1,
)
def expire_orders_job():
    ttl = timedelta(minutes=getattr(settings, "ORDER_PENDING_TTL_MINUTES", 15))
    expire_overdue_orders(ttl)

register_events(scheduler)

def start():
    if not scheduler.running:
        scheduler.start()