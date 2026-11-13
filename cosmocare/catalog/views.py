from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category

def home(request):
    featured = Product.objects.filter(is_active=True, is_featured=True)[:8]
    latest = Product.objects.filter(is_active=True).order_by("-created_at")[:8]
    categories = Category.objects.all()[:6]
    return render(request, "catalog/home.html", {"featured": featured, "latest": latest, "categories": categories})

def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    skin = request.GET.get("skin", "")
    sort = request.GET.get("sort", "")
    if q: 
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(ingredients__icontains=q))
    if category: 
        products = products.filter(category__slug=category)
    if skin: 
        products = products.filter(skin_type__icontains=skin)
    if sort == "price_low": 
        products = products.order_by("sale_price", "price")
    elif sort == "price_high": 
        products = products.order_by("-sale_price", "-price")
    categories = Category.objects.all()
    return render(request, "catalog/product_list.html", {"products": products, "categories": categories, "q": q})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "catalog/product_detail.html", {"product": product})
