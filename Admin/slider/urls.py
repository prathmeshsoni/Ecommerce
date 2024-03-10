from django.urls import path

from . import views

urlpatterns = [
    path('', views.slider),
    path('updateSlider/', views.updateSlider),
    path('remove_slider/<int:hid>', views.remove_slider),
]
