from django.db import models
from django.contrib.auth.models import User

class MistralAPI(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    counter_id = models.CharField(max_length=20)
    prompt = models.TextField()
    response = models.TextField()
    charts_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.user.email} - Prompt: {self.prompt[:50]}..."