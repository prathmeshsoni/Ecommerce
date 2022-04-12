from django.contrib import admin

def has_superuser_permission(request):
    return request.user.is_active and request.user.is_superuser

# Only active superuser can access root admin site (default)
admin.site.has_permission = has_superuser_permission