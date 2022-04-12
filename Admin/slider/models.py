from django.db import models


class GalleryModel(models.Model):
    slider_img = models.ImageField(upload_to = 'Admin/SliderImage')