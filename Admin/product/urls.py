from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('getdata/', views.getdata),
    path('updatepro/', views.updatepro),
    path('remove_pro/<int:hid>', views.remove_pro),
]
