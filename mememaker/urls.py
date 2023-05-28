# memegenerator/urls.py
from django.urls import path
from mememaker import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('mkmeme/', views.make_meme, name='mkmeme'),
    path('logout/', views.logout_page, name='logout'),
    path('community/',views.community_page, name='community'),
    path('myaccount/', views.account_page, name='account'),
    path('forgot_password/', views.forgot_pass, name='forgot_password'),
    path('emailsent', views.password_reset_email_sent, name='passdone'),
]
