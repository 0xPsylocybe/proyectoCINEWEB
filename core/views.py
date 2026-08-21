from django.shortcuts import render

def inicio(request):
    return render(request, "core/inicio.html")

def sobrecine(request):
    return render(request, "core/sobrecine.html")

def proximos_estrenos(request):
    return render(request, "core/proximos_estrenos.html")