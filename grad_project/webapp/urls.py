from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_screen),
    path('process-form/', views.process_form, name='process_form'),
    path('results/', views.result, name='result'),
]