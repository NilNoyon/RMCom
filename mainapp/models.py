from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
# Create your models here.

class CommonAction(models.Model):
     created_by = models.ForeignKey(User, related_name="%(class)s_created_by", related_query_name="%(class)s_created_by", 
                                        on_delete=models.CASCADE, null=True, blank=True, default=None)
     created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
     class Meta: abstract = True

class CommonActionWithUpdate(CommonAction):
     updated_by = models.ForeignKey(User, related_name="%(class)s_updated_by", related_query_name="%(class)s_updated_by", 
                                             on_delete=models.CASCADE, null=True, blank=True, default=None)
     updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
     class Meta: abstract = True


class TypeMaster(models.Model):
     value          = models.CharField(max_length=100)
     ordering       = models.IntegerField(default=0)
     status         = models.BooleanField(default=True)
     created_at     = models.DateTimeField(auto_now_add=True)

     class Meta:
          db_table = 'type_master'
          verbose_name = "Type Master"
          verbose_name_plural = "Type Master" 

     def __str__(self):
          return '%s' % (self.value)


class CommonMaster(models.Model): #this common model/table will use for all small master tables
     value          = models.CharField(max_length=120)
     value_for      = models.ForeignKey(TypeMaster,on_delete=models.CASCADE,null=True)
     ordering       = models.IntegerField(default=0)
     created_at     = models.DateTimeField(auto_now_add=True)
     status         = models.BooleanField(default = True)

     class Meta:
          db_table = 'common_master'
          verbose_name = "Master"
          verbose_name_plural = "Common Master" 

     def __str__(self):
          return '%s' % (self.value)

     @classmethod
     def name(self, name=''):
          try: return self.objects.get(value = name)
          except CommonMaster.DoesNotExist: return None
    
class Customer(models.Model):
     user         = models.OneToOneField(User,on_delete=models.CASCADE,related_name='customer')
     profile_pic  = models.ImageField(upload_to='profile_pic/CustomerProfilePic/',null=True,blank=True)
     address      = models.CharField(max_length=250)
     mobile       = models.CharField(max_length=20,null=False)

     @property
     def get_name(self):
          return self.user.first_name+" "+self.user.last_name
     @property
     def get_id(self):
          return self.user.id
     def __str__(self):
          return self.user.first_name


class Category(models.Model):
     name           = models.CharField(max_length=100, unique=True)
     short_name     = models.CharField(max_length=4, unique=True)
     description    = models.CharField(max_length=200, null=True, blank=True)
     category_type  = models.ForeignKey(TypeMaster,on_delete=models.CASCADE,null=True,related_name='category_type')

     def save(self, *args, **kwargs):
          self.short_name = self.short_name.upper()
          super(Category, self).save(*args, **kwargs)

     def __str__(self):
          return '%s' % (self.name)

     class Meta:
          db_table            = 'categories'
          verbose_name        = "Category"
          verbose_name_plural = "Categories"

     @staticmethod
     def get_name_wise_last_data(value):
          data_query = Category.objects.filter(name__iexact=value.strip())
          return data_query.last() if data_query.exists() else None

class SubCategory(models.Model):
     category            = models.ForeignKey(Category, on_delete=models.CASCADE)
     name                = models.CharField(max_length = 100, unique=True)
     short_name          = models.CharField(max_length = 4, unique=True)
     description         = models.CharField(max_length=200, null=True, blank=True)

     def save(self, *args, **kwargs):
          self.short_name = self.short_name.upper()
          super(SubCategory, self).save(*args, **kwargs)

     def __str__(self):
          return '%s - %s' % (self.category, self.name)

     class Meta:
          db_table            = 'subcategories'
          verbose_name        = "Sub-Category"
          verbose_name_plural = "Sub-Categories"

     @staticmethod
     def get_name_wise_last_data(value):
          data_query = SubCategory.objects.filter(name__iexact=value.strip())
          return data_query.last() if data_query.exists() else None
    

class Product(CommonActionWithUpdate):
     name           = models.CharField(max_length=50)
     code           = models.CharField(max_length=50, unique=True)
     product_image  = models.ImageField(upload_to='product_image/',null=True,blank=True)
     price          = models.FloatField()
     discount_price = models.FloatField(default=0)
     subcategory    = models.ForeignKey(SubCategory,on_delete=models.CASCADE,null=True,related_name='product_subcategory')
     description    = models.CharField(max_length=200)
     unit           = models.CharField(max_length=20,null=True,blank=True)

     class Meta:
          db_table            = 'product'
          verbose_name        = "Products"
          verbose_name_plural = "Products"

     def __str__(self):
          return self.name


class Order(models.Model):
     STATUS =(
          ('Pending','Pending'),
          ('Order Confirmed','Order Confirmed'),
          ('Out for Delivery','Out for Delivery'),
          ('Delivered','Delivered'),
          ('Cancelled','Cancelled'),
          ('Returned','Returned'),
     )
     order_number   = models.CharField(max_length=50, unique=True)
     customer       = models.ForeignKey(Customer, on_delete=models.CASCADE,null=True,blank=True,related_name='customer')
     email          = models.CharField(max_length=50,null=True)
     address        = models.CharField(max_length=500,null=True)
     mobile         = models.CharField(max_length=20,null=True)
     bill_amount    = models.FloatField()
     discount       = models.FloatField()
     total          = models.FloatField()
     payment        = models.ForeignKey(CommonMaster,on_delete=models.CASCADE,null=True,blank=True,related_name='payment')
     shipment       = models.ForeignKey(CommonMaster,on_delete=models.CASCADE,null=True,blank=True,related_name='shipment')
     order_date     = models.DateTimeField(auto_now_add=True,null=True)
     status         = models.CharField(max_length=50,null=True,choices=STATUS)
     transaction_id = models.CharField(max_length=100, blank=True, null=True)

     class Meta:
          db_table            = 'order'
          verbose_name        = "Orders"
          verbose_name_plural = "Orders"

     def __str__(self):
          return self.id
     
class OrderDetails(CommonActionWithUpdate):
     order          = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_details")
     product        = models.ForeignKey(Product, on_delete=models.CASCADE,null=True,blank=True,related_name='product')
     price          = models.FloatField()
     discount_price = models.FloatField()
     quantity       = models.FloatField()
     unit           = models.CharField(max_length=20,null=True,blank=True)
     subtotal       = models.FloatField()

     def save(self, *args, **kwargs):
        self.subtotal = round(self.quantity * self.price,3)
        super().save(*args, **kwargs)

     def __str__(self):
        return self.order.order_no + ' - ' + self.product

     class Meta:
          db_table            = 'order_details'
          verbose_name        = "Order Details"
          verbose_name_plural = "Order Details"

     def __str__(self):
          return self.id
     



class Feedback(CommonActionWithUpdate):
     user      = models.ForeignKey(Customer, on_delete=models.CASCADE,null=True,blank=True,related_name='feedback_from_customer')
     feedback  = models.CharField(max_length=500)
     ratings   = models.FloatField(default=5)

     class Meta:
          db_table            = 'feedback'
          verbose_name        = "Feedbacks"
          verbose_name_plural = "Feedbacks"

     def __str__(self):
          return self.users



class Campaign(CommonActionWithUpdate):
    class CampaignType(models.TextChoices):
        SEASONAL        = "seasonal", _("Seasonal")
        FLASH_SALE      = "flash_sale", _("Flash Sale")
        CLEARANCE       = "clearance", _("Clearance")
        BUY_ONE_GET_ONE = "bogo", _("Buy One Get One")

    class DiscountType(models.TextChoices):
        PERCENTAGE    = "percentage", _("Percentage")
        FIXED_AMOUNT  = "fixed_amount", _("Fixed Amount")
        FREE_SHIPPING = "free_shipping", _("Free Shipping")

    name           = models.CharField(max_length=255, unique=True)
    description    = models.TextField(blank=True, null=True)
    campaign_type  = models.CharField(max_length=50, choices=CampaignType.choices)
    discount_type  = models.CharField(max_length=50, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Percentage or Fixed Amount")
    min_purchase_amount   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Minimum order amount for eligibility")
    
    applicable_products   = models.ManyToManyField('Product', blank=True, related_name="campaigns")
    applicable_categories = models.ManyToManyField('Category', blank=True, related_name="campaigns")
    
    start_date  = models.DateTimeField()
    end_date    = models.DateTimeField()
    is_active   = models.BooleanField(default=True)

    def __str__(self):
        return self.name

