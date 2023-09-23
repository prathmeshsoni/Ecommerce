from django.db import models
from Admin.product.models import productModel
from Admin.address_master.models import stateModel
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE,null=True)
    auth_token = models.CharField(max_length=100,null=True )
    is_verified = models.BooleanField(default=False,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.user.username



# # Order
# status_choice=(
#         ('process','In Process'),
#         ('shipped','Shipped'),
#         ('delivered','Delivered'),
#     )
# class CartOrder(models.Model):
#     user=models.ForeignKey(User,on_delete=models.CASCADE)
#     total_amt=models.FloatField()
#     paid_status=models.BooleanField(default=False)
#     order_dt=models.DateTimeField(auto_now_add=True)
#     order_status=models.CharField(choices=status_choice,default='process',max_length=150)

#     class Meta:
#         verbose_name_plural='8. Orders'

class add_to_cart(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE,null=True)
    product_id = models.ForeignKey(productModel,on_delete=models.CASCADE,null=True )
    quantity = models.IntegerField(null=True)

    def __str__(self):
        return self.user.username

class addressModel(models.Model):
    #after change
    phone_number = models.BigIntegerField(null=True )
    first_name = models.CharField(max_length=30,null=True)
    last_name = models.CharField(max_length=30,null=True)
    locality = models.TextField(null = True)
    #after change
    user_id = models.ForeignKey(User ,on_delete=models.CASCADE)
    street_address = models.TextField(null = True)
    state = models.ForeignKey(stateModel,on_delete = models.CASCADE,null = True,blank = True)
    city = models.CharField(max_length=30,null=True)
    country = models.CharField(max_length=30,null=True)
    pincode = models.IntegerField(null=True)

    def __str__(self):
        return self.user_id.username


class buyModel(models.Model):
    user_id = models.ForeignKey(User ,on_delete=models.CASCADE,null=True)
    address_id = models.ForeignKey(addressModel,on_delete=models.CASCADE,null=True)
    payment_mode = models.CharField(max_length=50,null=True)
    order_date = models.DateField(blank=True,null=True)
    shipping_charge = models.IntegerField(null=True)
    total_quantity = models.IntegerField(null=True)
    total_amount = models.IntegerField(null=True)
    order_status = models.CharField(default='pending',max_length=20,blank=True,null=True)
    transaction_id = models.CharField(max_length=30,blank=True,null=True)
    order_idd = models.IntegerField(null=True)

    def __str__(self):
        return self.user_id.username


class Sub_bayModel(models.Model):
    order_id = models.ForeignKey(buyModel,on_delete=models.CASCADE)
    product_id = models.ForeignKey(productModel,on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField(null=True)
    total = models.IntegerField(null=True)

    def __str__(self):
        return self.product_id