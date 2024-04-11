"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an implogin_timerort:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib.auth import views as auth_views
from django.urls import path, include

from .views import *

urlpatterns = [
    path('', dashboard),
    path('login_timer/', some_view),
    path('loginurl/', geturl),
    path('logout/', logout),
    path('category/', include('Admin.category.urls')),
    path('brand/', include('Admin.subcategory.urls')),
    path('product/', include('Admin.product.urls')),
    path('slider/', include('Admin.slider.urls')),
    path('filter/', include('Admin.filter.urls')),
    path('order/', include('Admin.order.urls')),
    path('address/', include('Admin.address_master.urls')),
    path('accounts/login/', login_attempt, name='login'),
    path('logoutt/',
         auth_views.LogoutView.as_view(),
         name='logout'
         ),
    path(
        'change-password/',
        auth_views.PasswordChangeView.as_view(
            template_name='admin/change-password-1.html',
            success_url='/admin/',
        ),
        name='change_password'
    ),

    path('password-reset/', passwardd,
         name='password_reset'
         ),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='admin/password_reset_confirm.html',
             success_url='/admin/password-reset-complete/'
         ),
         name='password_reset_confirma'
         ),

    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='admin/password_reset_complete.html'
         ),
         name='password_reset_complete'
         ),
]
