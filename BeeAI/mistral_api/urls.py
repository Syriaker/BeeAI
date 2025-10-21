from django.urls import path
from .views import MistralAPIView, MetrikaAPIView, AnalysisHistoryView, AnalysisDetailView
from . import views

urlpatterns = [
    path('api/analyze/', views.MetrikaAPIView.as_view(), name='analyze'),
    path('api/generate/', views.MistralAPIView.as_view(), name='generate'),
    path('api/history/', views.AnalysisHistoryView.as_view(), name='analysis-history'),
    path('api/history/<int:pk>/', views.AnalysisDetailView.as_view(), name='analysis-history-detail'),
]