from django.urls import path
from . import views

urlpatterns=[
    path("",views.inicio, name="inicio"),
    path("sobrecine/",views.sobrecine,name="sobrecine"),
    path("informacion/",views.informacion,name="informacion"),
    ]