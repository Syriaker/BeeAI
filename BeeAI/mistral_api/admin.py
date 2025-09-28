from django.contrib import admin
from .models import MistralAPI

@admin.register(MistralAPI)
class MistralAPIAdmin(admin.ModelAdmin):
    list_display = ['id', 'prompt', 'response', 'created_at']
    list_filter = ['created_at']
    search_fields = ['prompt', 'response']
