"""MathPrepPro URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from AppOne import views
from rest_framework import routers
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('',views.index),
    path('admin/', admin.site.urls),
    path('list/', views.ProblemListView.as_view(), name = 'problem_list'),
    path('create/',views.ProblemCreateView.as_view(), name ='create'),
    path('list/<pk>/', views.ProblemDetailView.as_view(), name='detail'),
    path('update/<pk>/', views.ProblemUpdateView.as_view(), name='update'),
    path('delete/<pk>/', views.ProblemDeleteView.as_view(), name='delete'),
    path('prolist/<token>/', views.ProListView.as_view(), name = 'pro_list'),
    path('prolist/<token>/<pk>/', views.ProDetailView.as_view(), name='pro_detail'),
    path('home/', views.home, name='home'),
]

urlpatterns += staticfiles_urlpatterns() # This will serve static images for dev only
