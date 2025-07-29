# notification_service/email/urls.py

from django.urls import path
from nic_notify.receive import receive_email_webhook

urlpatterns = [
    path("receive/", receive_email_webhook, name="receive_email_webhook"),
]
