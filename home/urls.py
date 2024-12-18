from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/<int:menu_id>/', views.update_rating, name='update_rating'),
    path('home/profile/', views.Profile, name='profile'),
    path('logout/', views.logout_view, name='logout'), # Tambahkan ini
    path('admin/topup/', views.topup_balance, name='topup_balance'),
    path('home/pembelian/', views.pembelian_page, name='pembelian_page'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:menu_id>/', views.add_to_cart), 
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
]