import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'R_dot.settings')
django.setup()

from main.models import Banner, Product, Type, Category, Subcategory

# Check existing records
print("Current records:")
print(f"Banners: {Banner.objects.count()}")
print(f"Products: {Product.objects.count()}")
print(f"Types: {Type.objects.count()}")
print(f"Categories: {Category.objects.count()}")
print(f"Subcategories: {Subcategory.objects.count()}")

# Create a Type if none exists
if Type.objects.count() == 0:
    fashion_type = Type.objects.create(name='Fashion')
    print(f"Created Type: {fashion_type.name}")
else:
    fashion_type = Type.objects.first()

# Create Gadget type
if not Type.objects.filter(name='Gadget').exists():
    gadget_type = Type.objects.create(name='Gadget')
    print(f"Created Type: {gadget_type.name}")

# Create a Category if none exists
if Category.objects.count() == 0:
    category = Category.objects.create(type=fashion_type, name='General')
    print(f"Created Category: {category.name}")
else:
    category = Category.objects.first()

# Create a Subcategory if none exists
if Subcategory.objects.count() == 0:
    subcategory = Subcategory.objects.create(category=category, name='All Products')
    print(f"Created Subcategory: {subcategory.name}")
else:
    subcategory = Subcategory.objects.first()

# Create a Banner if none exists
if Banner.objects.count() == 0:
    banner = Banner.objects.create(
        title='Welcome to R-dot',
        subtitle='Shop the best products',
        image='banners/3_ukYVFzG.jpg',
        type=fashion_type
    )
    print(f"Created Banner: {banner.title} with image {banner.image}")
else:
    banner = Banner.objects.first()
    if banner:
        print(f"Existing Banner: {banner.title} with image {banner.image}")

# Create a Product if none exists
if Product.objects.count() == 0:
    product = Product.objects.create(
        subcategory=subcategory,
        name='Sample Fashion Product',
        image='products/E96A_blk.png',
        price=999.00,
        discount_price=799.00,
        description='This is a sample fashion product description with sizes'
    )
    product.is_fashion = True
    product.available_sizes = ['S', 'M', 'L', 'XL', '2XL']
    product.save()
    print(f"Created Fashion Product: {product.name} with sizes {product.available_sizes}")
else:
    product = Product.objects.first()
    if product:
        product.is_fashion = True
        product.available_sizes = ['S', 'M', 'L', 'XL', '2XL']
        product.save()
        print(f"Updated existing Product: {product.name} to Fashion with sizes {product.available_sizes}")

print("\nDone! Media files are now linked to database records.")
