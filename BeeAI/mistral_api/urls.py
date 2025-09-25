from django.urls import path
from .views import MistralAPIView, MetrikaAPIView
from . import views

urlpatterns = [
    path('api/analyze/', views.MetrikaAPIView.as_view(), name='analyze'),
    path('api/generate/', views.MistralAPIView.as_view(), name='generate'),
]