from django.shortcuts import render

# Create your views here.
def estudiantes_main(request):
    return render(request, 'estudiantes_main.html')