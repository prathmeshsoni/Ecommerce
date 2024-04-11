from django.urls import path

from . import views

urlpatterns = [
    path('', views.brand_page),
    path('updatebrand/', views.updatebrand),
    path('remove_brand/<int:hid>', views.remove_brand),
]
