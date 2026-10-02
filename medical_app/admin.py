from django.contrib import admin
from .models import * #Medical_Category, Medical_Product, Medical_Favourite, Medical_Cart, Medical_Address, Madical_Order, OrderItem

# Register your models here.
admin.site.register(Medical_Category)
admin.site.register(Medical_Product)
admin.site.register(Medical_Favourite)
admin.site.register(Medical_Cart)
admin.site.register(Medical_Address)
admin.site.register(Madical_Order)
admin.site.register(OrderItem)