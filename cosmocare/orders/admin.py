from django.contrib import admin
from .models import Order, OrderItem, Payment
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "unit_price", "quantity")
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "total", "payment_method", "payment_status", "status", "created_at")
    list_filter = ("status", "payment_status", "payment_method")
    search_fields = ("order_number", "user__username", "phone")
    inlines = [OrderItemInline]
admin.site.register(Payment)
