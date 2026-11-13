def cart_summary(request):
    if request.user.is_authenticated:
        items = request.user.cart_items.select_related("product")
        return {"nav_cart_count": sum(i.quantity for i in items)}
    return {"nav_cart_count": 0}
