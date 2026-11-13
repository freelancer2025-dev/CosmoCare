import hashlib, hmac, json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from orders.models import Order, Payment
from .services import verify_checkout_signature
from notifications.services import generate_order_qr, send_order_whatsapp

@login_required
def payment_checkout(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    payment = get_object_or_404(Payment, order=order)
    return render(request, "payments/checkout.html", {
                                                        "order": order, 
                                                        "payment": payment,
                                                        "razorpay_key": settings.RAZORPAY_KEY_ID
                                                    })

@login_required
@require_POST
def verify_payment(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    payment = get_object_or_404(Payment, order=order)
    pid = request.POST.get("razorpay_payment_id", "")
    oid = request.POST.get("razorpay_order_id", "")
    sig = request.POST.get("razorpay_signature", "")
    try:
        if oid != payment.gateway_order_id: 
            raise ValueError("Payment order mismatch")
        verify_checkout_signature(payment, pid, oid, sig)
    except Exception:
        messages.error(request, "Payment verification failed. Contact support before retrying.")
        return redirect("order_detail", order_number=order.order_number)
    payment.gateway_payment_id, payment.signature, payment.raw_status = pid, sig, "signature_verified"
    payment.save()
    order.payment_status = Order.PaymentStatus.PAID
    order.status = Order.Status.PLACED
    order.save()
    generate_order_qr(order)
    send_order_whatsapp(order, event="paid")
    return redirect("order_success", order_number=order.order_number)

@csrf_exempt
@require_POST
def razorpay_webhook(request):
    secret = settings.RAZORPAY_WEBHOOK_SECRET
    if not secret: 
        return HttpResponseBadRequest("Webhook secret not configured")
    signature = request.headers.get("X-Razorpay-Signature", "")
    expected = hmac.new(secret.encode(), request.body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature): 
        return HttpResponseBadRequest("Invalid signature")
    try:
        payload = json.loads(request.body)
        event = payload.get("event")
        entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = entity.get("order_id")
        payment_id = entity.get("id", "")
        payment = Payment.objects.select_related("order").get(gateway_order_id=order_id)
        order = payment.order
        if event == "payment.captured":
            payment.gateway_payment_id = payment_id
            payment.raw_status = "captured"
            payment.save()
            if order.payment_status != Order.PaymentStatus.PAID:
                order.payment_status = Order.PaymentStatus.PAID
                order.status = Order.Status.PLACED
                order.save()
                generate_order_qr(order)
                send_order_whatsapp(order, event="paid")
        elif event == "payment.failed":
            payment.raw_status = "failed"
            payment.save()
            if order.payment_status != Order.PaymentStatus.PAID:
                order.payment_status = Order.PaymentStatus.FAILED
                order.save()
    except Payment.DoesNotExist:
        pass
    except Exception:
        return HttpResponseBadRequest("Webhook processing error")
    return HttpResponse("ok")
