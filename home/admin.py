from django.contrib import admin
from . import models


# Register your models here.
class ProductImageAdmin(admin.TabularInline):
    model = models.ProductImage


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]


admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Category)
admin.site.register(models.Cart)
admin.site.register(models.Section)
admin.site.register(models.Size)


class OrderItemAdmin(admin.TabularInline):
    model = models.OrderItem


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemAdmin]


admin.site.register(models.Order, OrderAdmin)
