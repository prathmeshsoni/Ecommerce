import os

from django.db import models

from Admin.category.models import categoryModel
from Admin.subcategory.models import brandModel


class productModel(models.Model):
    id = models.AutoField(primary_key=True)
    catname_id = models.ForeignKey(categoryModel, on_delete=models.CASCADE, null=True, related_name='product_rel')
    brand = models.ForeignKey(brandModel, on_delete=models.CASCADE, null=True)
    productname = models.CharField(max_length=50)
    pro_description = models.TextField(null=True)
    pro_code = models.IntegerField(null=True)

    total_quantity = models.IntegerField(null=True)
    pro_price = models.IntegerField(null=True, blank=True)
    strike_price = models.IntegerField(null=True, blank=True)

    pro_colour = models.CharField(max_length=50)
    return_product = models.CharField(max_length=6, null=True)
    return_period_days = models.IntegerField(null=True)

    pro_height = models.IntegerField(null=True)
    pro_width = models.IntegerField(null=True)
    pro_length = models.IntegerField(null=True)

    pro_image = models.ImageField(upload_to='Admin/ProductImage/Main', default='default.jpg', null=True, blank=True)
    pro_back_image = models.ImageField(upload_to='Admin/ProductImage/Back', default='default.jpg', null=True,
                                       blank=True)
    feature_image = models.ImageField(upload_to='Admin/ProductImage/Feature', default='default.jpg', null=True,
                                      blank=True)

    def delete(self, *args, **kwargs):
        # Delete the image file when the product is deleted
        for field in ['pro_image', 'pro_back_image', 'feature_image']:
            file = getattr(self, field)
            if file:
                os.remove(file.path)
        super(productModel, self).delete(*args, **kwargs)

    def __str__(self):
        return "%s" % self.productname
