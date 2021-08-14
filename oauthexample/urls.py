from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.index),
    path('noexit/callback/', views.callback),
    path('profile/', views.profile),
    path('refresh/', views.manual_refresh),
    path('autologin/', views.auto_login),
]