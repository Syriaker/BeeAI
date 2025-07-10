from django.urls import path
from .views import MistralAPIView

urlpatterns = [
    path('generate/', MistralAPIView.as_view(), name='mistral_generate'),
]