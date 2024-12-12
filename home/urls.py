from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/<int:menu_id>/', views.menu_detail, name='menu_detail'),
    path('home/', views.home, name='home'), 
    path('home/profile/', views.Profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
]