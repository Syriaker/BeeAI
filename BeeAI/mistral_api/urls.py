from django.urls import path
from .views import MistralAPIView, MetrikaAPIView
from . import views

urlpatterns = [
    path('', views.my_view, name='my_view'),
    path('generate/', MistralAPIView.as_view(), name='mistral_generate'),
    path('metrika/', MetrikaAPIView.as_view(), name='metrika_api'),
]