# email/receive.py

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from nic_notify.models import NotificationLog

@csrf_exempt
def receive_email_webhook(request):
    if request.method == "POST":
        from_email = request.POST.get("from")
        to_email = request.POST.get("to")
        subject = request.POST.get("subject", "")
        body = request.POST.get("text") or request.POST.get("body-plain")

        if not (from_email and to_email and body):
            return JsonResponse({"error": "Missing data"}, status=400)

        NotificationLog.objects.create(
            notification_type="email",
            sent_from=from_email,
            sent_to=to_email,
            message=f"Subject: {subject}\n\n{body}",
            status="received"
        )

        return HttpResponse("OK", status=200)

    return HttpResponse("Method Not Allowed", status=405)
