from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
import uuid


class Medical_Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    category_slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    category_desc = models.TextField(blank=True, null=True)
    category_image = models.ImageField(upload_to="categorise/", blank=True, null=True)
    category_created_at = models.DateTimeField(auto_now_add=True)
    
   

    
    def save(self, *args, **kwargs):
        self.category_slug = slugify(self.category_name)
        super().save(*args, **kwargs)
        
    
    def __str__(self):
        return self.category_name

''' 
created product Model
'''

class Medical_Product(models.Model):
    product_category = models.ForeignKey (Medical_Category, on_delete = models.CASCADE, related_name="products")
    product_name = models.CharField (max_length=150, unique=True)
    product_slug = models.SlugField (max_length=150, unique=True, blank=True, null=True)
    product_image = models. ImageField(upload_to="products/", null=True, blank=True)
    product_description = models.TextField()
    product_price = models. DecimalField(max_digits=10, decimal_places=2)
    product_quantity_in_stock = models. IntegerField (max_length=10)
    product_is_active = models. BooleanField (default=True)
    product_is_featured = models. BooleanField (default=False)
    product_created_at = models. DateTimeField(auto_now_add=True)
    
    
    def save(self, *args, **kwargs):
        self.category_slug = slugify(self.product_name)
        super().save(*args, **kwargs)
            
        
    def __str__(self):
        return self.product_name
    

''' 
created favourites Model
'''
class Medical_Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='favourites')
    product = models.ForeignKey(Medical_Product, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    
    def __str__(self):
            return f"{self.user} -> {self.product}"
        
        
class Medical_Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    product = models.ForeignKey(Medical_Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} -> {self.product} -> {self.quantity}"



'''
Creating Address Model
-> makemigrations migrate
'''



class Medical_Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Customer Information
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    # Delivery Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    landmark = models.CharField(max_length=100)
    address_type = models.CharField(max_length=100)
    # Default Address
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} -> {self.city}"

    
'''
Creating Order Model
-> makemigrations migrate
'''

class Madical_Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orderb')
    order_id = models.CharField(max_length=250, default= uuid.uuid4, null=True, blank=True)
    shipping_address = models.ForeignKey(Medical_Address, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2) #2399.23
    payment_mode = models.CharField(max_length=100, choices=(('cod', 'Cash On Delevery'), ('online', 'Online Payment')), default='cod')
    payment_status = models.CharField(max_length=100, choices=(('pending','Pending'), ('processing','Processing'), ('completed', 'Completed'), ('faild', 'Faild'), ('cancle', 'Cancle')))
    tracking_no = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    razorpay_order_id = models.CharField(max_length=250, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=250, null=True, blank=True)
    razorpay_signeture = models.CharField(max_length=250, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user} -> {self.order_id}"
    


'''
Creating OrderItem Model
-> makemigrations migrate
'''

class OrderItem(models.Model):
    order = models.ForeignKey(Madical_Order, on_delete=models.CASCADE, related_name='orderitems')
    product = models.ForeignKey(Medical_Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    
    
    def __str__(self):
        return f"{self.order.order_id} -> {self.product.product_name}"