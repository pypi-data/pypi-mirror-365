from django.urls import path
from . import views


urlpatterns = [
    path('registration/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('token/refresh/', views.custom_token_refresh_view, name='token_refresh'),
    path('logout/', views.logout_view, name='logout'),
]
