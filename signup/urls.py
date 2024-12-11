from django.urls import path
from .views import signup_view
from home.views import home


urlpatterns = [
    path('', signup_view, name='signup'),
    path('home/', home, name='home'),
]
