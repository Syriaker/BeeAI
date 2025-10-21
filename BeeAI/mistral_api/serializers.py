from rest_framework import serializers
from .models import MistralAPI

class AnalysisHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MistralAPI
        fields = ('id', 'counter_id', 'created_at')

class AnalysisDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MistralAPI
        fields = ('id', 'counter_id', 'created_at', 'response', 'charts_data')
