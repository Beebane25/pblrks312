from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/<int:menu_id>/', views.menu_detail, name='menu_detail'),
]