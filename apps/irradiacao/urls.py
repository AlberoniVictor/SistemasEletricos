from django.urls import path
from . import views

urlpatterns = [
    path('buscar/', views.buscar_irradiacao, name='buscar_irradiacao'),
]
