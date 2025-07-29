# notification_service/whatsapp/urls.py

from django.urls import path
from nic_notify.receive import receive_whatsapp_webhook

urlpatterns = [
    path("receive/", receive_whatsapp_webhook, name="receive_whatsapp_webhook"),
]
