import razorpay
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from orders.models import Payment

def get_client():
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise ImproperlyConfigured("Razorpay keys are missing from .env")
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_razorpay_order(order):
    client = get_client()
    amount = int(order.total * 100)
    result = client.order.create({"amount": amount, "currency": settings.DEFAULT_CURRENCY,
                                  "receipt": order.order_number,
                                  "notes": {"cosmocare_order": order.order_number}})
    Payment.objects.update_or_create(order=order, defaults={
        "gateway_order_id": result["id"], "amount_paise": amount, "raw_status": result.get("status", "created")
    })
    return result

def verify_checkout_signature(payment, razorpay_payment_id, razorpay_order_id, signature):
    client = get_client()
    client.utility.verify_payment_signature({
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": signature,
    })
