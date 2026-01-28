from django.contrib import admin
from .models import Product, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price_jpy", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "customer_email", "total_jpy", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("customer_email", "customer_name", "stripe_checkout_session_id")
    inlines = [OrderItemInline]
