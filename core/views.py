from django.shortcuts import render

def inicio(request):
    return render(request, "core/inicio.html")

def sobrecine(request):
    return render(request, "core/sobrecine.html")

def informacion(request):
    return render(request, "core/informacion.html")