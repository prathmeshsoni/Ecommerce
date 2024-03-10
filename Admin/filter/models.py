from django.db import models


class colourModel(models.Model):
    colour_name = models.CharField(max_length=20)
    colour_image = models.ImageField(upload_to='Admin/Colour Image')

    def __str__(self):
        return "%s" % (self.colour_name)
