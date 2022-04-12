from django.db import models

class categoryModel(models.Model):
    cat_name = models.CharField(max_length=30,null =True )
    cat_img = models.ImageField(null =True ,upload_to = 'Admin/categoryImage')

    def __str__(self):
        return "%s" % (self.cat_name)