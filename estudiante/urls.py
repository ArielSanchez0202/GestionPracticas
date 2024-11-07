from django.urls import path
from . import views

app_name = 'estudiante'

urlpatterns = [
 path('estudiantes_main/', views.estudiantes_main, name='estudiantes_main'),
    path('agregar/', views.agregar_practica, name='agregar_practica'),
    path('listar/', views.listar_practicas, name='listar_practicas'),
]