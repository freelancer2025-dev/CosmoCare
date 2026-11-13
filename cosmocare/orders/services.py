from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Order, OrderItem
from cart.models import CartItem

def create_order_from_cart(user, address, method):
    with transaction.atomic():
        cart_items = list(CartItem.objects.select_for_update().filter(user=user).select_related("product"))
        if not cart_items:
            raise ValidationError("Your cart is empty.")
        subtotal = sum((item.product.current_price * item.quantity for item in cart_items), start=0)
        shipping = 0 if subtotal >= 999 else 49
        order = Order.objects.create(
            user=user, full_name=address.full_name, phone=address.phone,
            email=user.email, address_text=f"{address.line1} {address.line2}, {address.city}, {address.state} - {address.pincode}",
            subtotal=subtotal, shipping=shipping, total=subtotal+shipping,
            payment_method=method, status=Order.Status.PENDING if method == "RAZORPAY" else Order.Status.PLACED,
            payment_status=Order.PaymentStatus.PENDING,
        )
        for item in cart_items:
            if item.quantity > item.product.stock:
                raise ValidationError(f"Insufficient stock for {item.product.name}.")
            OrderItem.objects.create(order=order, product=item.product, product_name=item.product.name,
                                     unit_price=item.product.current_price, quantity=item.quantity)
            item.product.stock -= item.quantity
            item.product.save(update_fields=["stock"])
        CartItem.objects.filter(user=user).delete()
        return order
