from django.shortcuts import render

def login(request):
    return render(request, "usuarios/login.html")

def loginout(request):
    return render(request, "usuarios/loginout.html")
