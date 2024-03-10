from django.contrib import admin

from .models import Profile, addressModel, buyModel, Sub_bayModel, add_to_cart

admin.site.register(Profile)
admin.site.register(addressModel)
admin.site.register(buyModel)
admin.site.register(Sub_bayModel)
admin.site.register(add_to_cart)
