from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.user_login, name='home'),
    path('change_password/', views.change_password, name='change_password'),
    path('password_reset/', views.custom_password_reset_request, name='custom_password_reset'),
    path('password_reset_done/', views.custom_password_reset_done, name='custom_password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', views.custom_password_reset_confirm, name='custom_password_reset_confirm'),
    path('password_reset_complete/', views.custom_password_reset_complete, name='custom_password_reset_complete'),
    path('logout/', views.user_logout, name='logout'),
    path('bloquear-usuario/<int:user_id>/', views.bloquear_usuario, name='bloquear_usuario'),
    path('desbloquear-usuario/<int:user_id>/', views.desbloquear_usuario, name='desbloquear_usuario'),
]