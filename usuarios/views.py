from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import RegistroUsuarioForm

def login(request):
    return render(request, "usuarios/login.html")

def logout(request):
    return render(request, "usuarios/logout.html")


def registro_usuario(request): 
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido a Cines León.')
            return redirect('inicio') 
    else:
        form = RegistroUsuarioForm()
    
    # Debe apuntar a su propia plantilla de registro, no al login
    return render(request, 'usuarios/registro.html', {'form': form})