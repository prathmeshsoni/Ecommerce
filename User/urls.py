from django.contrib import admin
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('accounts/login/' , login_attempt , name="login_attempt"),
    path('logout/', logout , name = 'logout'),

    path('register' , register_attempt , name="register_attempt"),
    path('token' , token_send , name="token_send"),
    path('verify/<auth_token>' , verify , name="verify"),

    path('password-reset/' , forget_passward , name="password_resett"),

    path('' ,  home  , name="home"),

    path('category/<int:hid>' , category ),
    path('category/' , cat_page ),

    path('product/<int:pid>' , product ),
    path('product/' , pro_page ),

    path('dashboard/' , dashboard ),

    path( 'address/', views.address ),
    path('myaccount/' , myaccount ),
    path('address/updete/', updateaddress ),
    path('address/remove/<int:hid>', remove_address ),

    path('myorder/' , myorder ),
    path('order/<int:hid>/<int:sid>' , myorder1 ),
    
    path('gocart/' , gocart ),
    path('cart/' , addCart ),

    path('checkout/', checkout ),
    path('success/' , payment_status , name='payment_status'),

    # path('password-reset/',
    #     auth_views.PasswordResetView.as_view(
    #         template_name='user/password_reset_form.html',
    #         # success_url='/login/'
    #     ),
    #     name='password_resett'
    # ),

    path('password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='user/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path('password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='user/password_reset_confirm.html'
        ),
        name='password_reset_confirmm'
    ),

    path('password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='user/password_reset_complete.html'
        ),
        name='password_reset_completee'
    ),
   
]


# handler404 = 'User.views.error_404'