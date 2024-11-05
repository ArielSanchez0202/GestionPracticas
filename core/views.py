from django.shortcuts import render, redirect

# Create your views here.
def listar_estudiantes(request):
    return render(request, 'listar_estudiantes.html', {'active_page': 'listar_estudiantes'})

def listar_coordinador(request):
    return render(request, 'listar_.coordinador.html', {'active_page': 'listar_coordinador'})

def estudiantes_main(request):
    if request.user.is_authenticated:
        # Si el usuario está autenticado, pasar el usuario a la plantilla
        return render(request, 'base_estudiante.html', {'user': request.user})
    else:
        # Redirigir o manejar el caso de usuario no autenticado
        return redirect('home')