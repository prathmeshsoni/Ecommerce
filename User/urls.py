from django.contrib.auth import views as auth_views
from django.urls import path

from .views import *

urlpatterns = [
    path('', home, name="home"),
    path('tracker/', tracker, name='tracker'),
    path('change-password/', change_password, name='change_passwordd'),
    path('accounts/login/', login_attempt, name="login_attempt"),
    path('logout/', logout, name='logout'),

    path('register/', register_attempt, name="register_attempt"),
    path('token', token_send, name="token_send"),
    path('verify/<auth_token>', verify, name="verify"),

    path('password-reset/', forget_password, name="password_resett"),

    path('quickview/', quickview),
    path('quickview1/', quickviesw),

    path('category/<int:hid>', category),
    path('category/', cat_page),

    path('product/<int:pid>', product),
    path('product/', pro_page),

    path('dashboard/', dashboard),

    path('address/', address),

    path('orderrrr/', myorderrr),
    path('myaccount/', myaccount),
    path('address/updete/', updateaddress),
    path('address/remove/', remove_address),

    path('myorder/', myorder),
    path('order/<int:hid>/<int:sid>', myorder1),

    path('gocart/', gocart),
    path('cart/', addCart),
    path('review/', review),

    path('checkout/', checkouut),
    path('success/', payment_status, name='payment_status'),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='user/password_reset_confirm.html',
             success_url='/user/password-reset-complete/'
         ),
         name='password_reset_confirmm'
         ),

    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='user/password_reset_complete.html'
         ),
         name='password_reset_complete'
         ),

]

# handler404 = 'User.views.error_404'
