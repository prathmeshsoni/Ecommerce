from django.urls import path

from . import views

urlpatterns = [
    path('colour/', views.colour),
    path('colour/updatecolour/', views.update_colour),
    path('colour/removecolour/<int:hid>', views.remove_colour),
]
