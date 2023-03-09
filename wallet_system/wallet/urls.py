from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('about', views.about, name="about"),
    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('profile/<str:pk>/', views.userProfile, name="profile"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('transactions/', views.transactions, name="transactions"),
    path('search/', views.search, name="search"),
    path('sendmoney/', views.sendMoney, name="sendmoney"),
    path('fundwallet/', views.fundWallet, name="fundwallet"),
    path('transfer/', views.transfer, name="transfer"),
    path('check_account/', views.checkAccount, name="check_account"),
    path('banks/', views.banks, name="banks"),
    path('webhook/', views.paystackWebhook, name="webhook"),]

