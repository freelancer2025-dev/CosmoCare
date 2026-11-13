import requests
import qrcode
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from django.urls import reverse

def generate_order_qr(order):
    tracking_url = f"{settings.SITE_BASE_URL}{reverse('order_detail', kwargs={'order_number': order.order_number})}?token={order.public_token}"
    image = qrcode.make(tracking_url)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    order.qr_image.save(f"{order.order_number}.png", ContentFile(buffer.getvalue()), save=True)
    return order.qr_image.url

def send_order_whatsapp(order, event="placed"):
    # Requires a WhatsApp-approved template for business-initiated messages.
    token = settings.WHATSAPP_TOKEN
    phone_id = settings.WHATSAPP_PHONE_NUMBER_ID
    template = settings.WHATSAPP_TEMPLATE_NAME
    if not (token and phone_id and template and order.phone):
        return False
    phone = "".join(ch for ch in order.phone if ch.isdigit())
    if len(phone) == 10: phone = "91" + phone
    base = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{phone_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    text = f"CosmoCare order {order.order_number}: {event}. Total ₹{order.total}. Status: {order.get_status_display()}."
    payload = {"messaging_product": "whatsapp", "to": phone, "type": "template",
               "template": {"name": template, "language": {"code": settings.WHATSAPP_LANGUAGE_CODE},
               "components": [{"type": "body", "parameters": [
                   {"type": "text", "text": order.full_name},
                   {"type": "text", "text": order.order_number},
                   {"type": "text", "text": f"₹{order.total}"},
                   {"type": "text", "text": text[:900]}
               ]}]}}
    try:
        response = requests.post(base, headers=headers, json=payload, timeout=15)
        return response.ok
    except requests.RequestException:
        return False
