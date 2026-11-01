from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0
    readonly_fields = ['price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'phone', 'status', 'total_cost', 'created_at']
    list_filter = ['status', 'created_at', 'updated_at']
    list_editable = ['status']
    search_fields = ['id', 'first_name', 'last_name', 'phone', 'email']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at', 'total_cost']