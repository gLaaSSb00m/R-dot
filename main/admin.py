from django.contrib import admin
from .models import Category, Banner, Product, Subcategory, NewOrder, Type

admin.site.register(Type)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Banner)
admin.site.register(Product)
admin.site.register(NewOrder)
