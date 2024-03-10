from django.db import models


class stateModel(models.Model):
    state_name = models.CharField(max_length=100)

    def __str__(self):
        return "%s" % self.state_name
