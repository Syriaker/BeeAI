from django.urls import path
from .views import RegistrationView, LoginView

urlpatterns = [
    path('api/register/', RegistrationView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
]