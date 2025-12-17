from django.db import models

class WebhookEvent(models.Model):
    event_id = models.CharField(max_length=100, unique=True)
    payload = models.JSONField()
    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event_id
