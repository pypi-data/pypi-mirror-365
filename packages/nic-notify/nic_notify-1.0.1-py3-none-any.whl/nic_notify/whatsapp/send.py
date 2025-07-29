# whatsapp/send.py
from twilio.rest import Client
import os

def send_whatsapp_message(to, message):
    client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    from_whatsapp_number = f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}"
    to_whatsapp_number = f"whatsapp:{to}"

    msg = client.messages.create(
        body=message,
        from_=from_whatsapp_number,
        to=to_whatsapp_number
    )
    return msg.sid
