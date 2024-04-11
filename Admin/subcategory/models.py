from django.db import models


class brandModel(models.Model):
    brand_name = models.CharField(max_length=30, null=True)

    def __str__(self):
        return "%s" % (self.brand_name)
