from django.db import models

class Banner(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=200)
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

class Type(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Category(models.Model):
    type = models.ForeignKey(Type, on_delete=models.CASCADE, related_name='categories', null=True, blank=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Product(models.Model):
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    discount_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    stock_out = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    related_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='blogs')

    def __str__(self):
        return self.title

class NewOrder(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField()
    mobile_number = models.CharField(max_length=15)
    product_code = models.CharField(max_length=100)  # Assuming product has a code, or use product.id
    product_name = models.CharField(max_length=200)
    product_image = models.ImageField(upload_to='order_products/')
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order for {self.product_name} by {self.user.username if self.user else 'Anonymous'}"
