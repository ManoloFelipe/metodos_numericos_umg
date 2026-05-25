from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('newton_raphson/', views.newton_raphson, name='newton_raphson'),
    path('taylor/', views.taylor, name='taylor'),
    path('coseno/', views.coseno, name='coseno'),
]
