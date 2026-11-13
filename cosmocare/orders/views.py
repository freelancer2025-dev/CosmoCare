from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from accounts.models import Address
from .models import Order
from .services import create_order_from_cart
from payments.services import create_razorpay_order
from notifications.services import generate_order_qr, send_order_whatsapp

@login_required
def checkout(request):
    addresses = request.user.addresses.all()
    if request.method == "POST":
        address = get_object_or_404(Address, pk=request.POST.get("address"), user=request.user)
        method = request.POST.get("payment_method", "COD")
        if method not in ("COD", "RAZORPAY"): 
            method = "COD"
        try:
            order = create_order_from_cart(request.user, address, method)
        except ValidationError as exc:
            messages.error(request, str(exc))
            return redirect("cart_detail")
        if method == "RAZORPAY":
            try:
                create_razorpay_order(order)
            except Exception:
                order.status = Order.Status.PENDING
                order.save(update_fields=["status"])
                messages.error(request, "Could not start Razorpay. Check gateway configuration and try again.")
                return redirect("order_detail", order_number=order.order_number)
            return redirect("payment_checkout", order_number=order.order_number)
        order.payment_status = Order.PaymentStatus.PENDING
        order.save()
        generate_order_qr(order)
        send_order_whatsapp(order, event="placed")
        return redirect("order_success", order_number=order.order_number)
    return render(request, "orders/checkout.html", {"addresses": addresses})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders/my_orders.html", {"orders": orders})

@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, "orders/order_detail.html", {"order": order})

@login_required
def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, "orders/order_success.html", {"order": order})

@login_required
@require_POST
def cancel_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    reason = request.POST.get("reason", "").strip()
    if order.status in (Order.Status.PENDING, Order.Status.PLACED, Order.Status.PROCESSING):
        if order.payment_status == Order.PaymentStatus.PAID:
            order.status = Order.Status.CANCEL_REQUESTED
            order.payment_status = Order.PaymentStatus.REFUND_PENDING
        else:
            order.status = Order.Status.CANCELLED
        order.cancellation_reason = reason
        order.save()
        # Refunds must be initiated/reconciled through the gateway/admin; do not mark refunded automatically.
        send_order_whatsapp(order, event="cancelled")
        messages.success(request, "Your cancellation request has been recorded.")
    else:
        messages.error(request, "This order can no longer be cancelled online.")
    return redirect("order_detail", order_number=order.order_number)
