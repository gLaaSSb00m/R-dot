from typing import Any
from django.contrib import admin
from django import forms
from .models import Category, Banner, Product, Subcategory, NewOrder, Type

admin.site.register(Type)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Banner)
admin.site.register(NewOrder)

SIZES = [('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('2XL', '2XL')]

class ProductAdminForm(forms.ModelForm):
    sizes = forms.MultipleChoiceField(
        choices=SIZES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Available Sizes (Fashion products only)'
    )

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        instance: Product | None = kwargs.get('instance')
        if instance and not instance.is_fashion:
            self.fields['sizes'].widget = forms.HiddenInput()
            self.initial['sizes'] = []
        elif not self.instance.is_fashion:
            self.fields['sizes'].widget = forms.HiddenInput()

    def save(self, commit: bool = True) -> Product:
        instance = super().save(commit=False)
        selected_sizes = self.cleaned_data.get('sizes', [])
        instance.available_sizes = list(selected_sizes)
        if commit:
            instance.save()
        return instance

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin[Product]):
    form = ProductAdminForm
    fieldsets = [
        ('Basic', {'fields': ['name', 'subcategory']}),
        ('Pricing', {'fields': ['price', 'discount_price']}),
        ('Inventory', {'fields': ['stock_out', 'is_fashion']}),
        ('Sizes', {'fields': ['sizes'], 'classes': ('collapse',)}),
        ('Media', {'fields': ['image']}),
        ('Content', {'fields': ['description']}),
    ]
    list_display = ['name', 'subcategory', 'is_fashion', 'available_sizes']
    list_filter = ['is_fashion', 'subcategory__category__type']
