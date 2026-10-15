from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard Home Overview
    path('', views.dashboard_home, name='home'),

    # Products Management
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('products/<int:pk>/toggle/', views.product_toggle_status, name='product_toggle'),

    # Categories Management
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('categories/<int:pk>/toggle/', views.category_toggle_status, name='category_toggle'),

    # Banners Management
    path('banners/', views.banner_list, name='banner_list'),
    path('banners/add/', views.banner_create, name='banner_create'),
    path('banners/<int:pk>/edit/', views.banner_edit, name='banner_edit'),
    path('banners/<int:pk>/delete/', views.banner_delete, name='banner_delete'),
    path('banners/<int:pk>/toggle/', views.banner_toggle_status, name='banner_toggle'),

    # Users Management
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:pk>/toggle/', views.user_toggle_status, name='user_toggle'),
]
