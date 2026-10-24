from django.contrib import admin
from .models import Category, MenuItem, Cart, Order, OrderItem

admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Cart)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "delivery_crew", "status", "total", "date")
    inlines = [OrderItemInline]
