import os

from django.db import models


class GalleryModel(models.Model):
    slider_img = models.ImageField(upload_to='Admin/SliderImage')

    def delete(self, *args, **kwargs):
        # Delete the image file when the product is deleted
        os.remove(self.slider_img.path)
        super(GalleryModel, self).delete(*args, **kwargs)
