from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', register, name='register'),
    path('verify_otp/<int:user_id>/', verify_otp, name='verify_otp'),
    path('profile/', profile, name='profile'),
    path('wallet_topup/', wallet_topup, name='wallet_topup'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
]
