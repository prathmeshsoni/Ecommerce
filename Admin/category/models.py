import os

from django.db import models


class categoryModel(models.Model):
    cat_name = models.CharField(max_length=30, null=True)
    cat_img = models.ImageField(null=True, upload_to='Admin/categoryImage')

    def delete(self, *args, **kwargs):
        # Delete the image file when the product is deleted
        os.remove(self.cat_img.path)
        super(categoryModel, self).delete(*args, **kwargs)

    def __str__(self):
        return "%s" % (self.cat_name)
