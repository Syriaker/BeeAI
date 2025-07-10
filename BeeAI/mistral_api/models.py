from django.db import models

class MistralAPI(models.Model):
    prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prompt: {self.prompt[:50]}... Response: {self.response[:50]}..."