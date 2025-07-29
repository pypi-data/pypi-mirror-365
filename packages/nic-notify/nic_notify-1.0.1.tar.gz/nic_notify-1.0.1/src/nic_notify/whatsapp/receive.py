from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils.timezone import now
from nic_notify.models import NotificationLog
import os

@csrf_exempt
def receive_whatsapp_webhook(request):
    if request.method == "POST":
        from_number = request.POST.get("From")  # e.g., whatsapp:+1234567890
        to_number = request.POST.get("To")      # e.g., whatsapp:+YOUR_BOT_NUMBER
        body = request.POST.get("Body")

        NotificationLog.objects.create(
            notification_type="whatsapp",
            sent_from=from_number,
            sent_to=to_number,
            message=body,
            status="received"
        )
        return HttpResponse("OK", status=200)

    return HttpResponse("Method Not Allowed", status=405)
