from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from catalog.models import Product
from .models import Review

@login_required
@require_POST
def add_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    rating = int(request.POST.get("rating", 5))
    if rating < 1 or rating > 5: 
        rating = 5
    Review.objects.update_or_create(user=request.user, product=product, 
        defaults={
                    "rating": rating, "title": request.POST.get("title", "")[:120],
                    "comment": request.POST.get("comment", "")
                })
    messages.success(request, "Your review has been saved.")
    return redirect("product_detail", slug=product.slug)
