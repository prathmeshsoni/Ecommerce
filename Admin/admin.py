from django.contrib import admin
from Admin.category.models import categoryModel
from Admin.subcategory.models import brandModel
from Admin.product.models import productModel
from Admin.address_master.models import stateModel
from Admin.slider.models import GalleryModel


admin.site.register(categoryModel)
admin.site.register(brandModel)
admin.site.register(productModel)
admin.site.register(stateModel)
admin.site.register(GalleryModel)

def has_superuser_permission(request):
    return request.user.is_active and request.user.is_superuser

# Only active superuser can access root admin site (default)
admin.site.has_permission = has_superuser_permission


