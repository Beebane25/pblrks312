from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/<int:menu_id>/', views.update_rating, name='update_rating'),
    path('home/profile/', views.Profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
]