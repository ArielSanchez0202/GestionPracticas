from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('base_coordinador/', views.base_coordinador, name='base_coordinador'),
]
