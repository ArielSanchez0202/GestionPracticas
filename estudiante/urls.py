from django.urls import path
from . import views

app_name = 'estudiante'

urlpatterns = [
 path('estudiantes_main/', views.estudiantes_main, name='estudiantes_main'),
]