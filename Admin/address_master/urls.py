from django.urls import path,include
from . import views

urlpatterns = [
    path('state/', views.state),
    path('state/updateState/', views.updateState),
    path('state/remove_state/<int:hid>', views.remove_state),

]