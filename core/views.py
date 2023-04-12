from django.shortcuts import render

# Página de Inicio
def home(request):
    return render(request, 'core/home.html')
