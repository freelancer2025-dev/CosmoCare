from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from catalog.models import Product
from .models import CartItem

@login_required
def cart_detail(request):
    items = request.user.cart_items.select_related("product")
    subtotal = sum(i.line_total for i in items)
    return render(request, "cart/cart.html", {"items": items, "subtotal": subtotal})

@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    qty = max(1, int(request.POST.get("quantity", 1)))
    item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    item.quantity = min(item.quantity + (0 if created else qty), product.stock) if not created else min(qty, product.stock)
    if product.stock > 0:
        item.save()
        messages.success(request, "Added to your cart.")
    else:
        messages.error(request, "This product is currently out of stock.")
    return redirect("cart_detail")

@login_required
@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, user=request.user)
    qty = int(request.POST.get("quantity", 1))
    if qty <= 0: item.delete()
    else:
        item.quantity = min(qty, item.product.stock)
        item.save()
    return redirect("cart_detail")

@login_required
@require_POST
def remove_from_cart(request, item_id):
    get_object_or_404(CartItem, pk=item_id, user=request.user).delete()
    return redirect("cart_detail")
