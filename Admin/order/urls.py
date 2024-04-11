from django.urls import path

from . import views

urlpatterns = [
    path('', views.order),
    path('<int:hid>', views.order_detail),
]
