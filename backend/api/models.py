from django.db import models
from django.contrib.auth.models import User
import uuid


class Circle(models.Model):
    name = models.CharField(max_length=100)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="admin_circles")
    invite_code = models.CharField(max_length=8, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name="members")
    position = models.PositiveIntegerField()

    class Meta:
        unique_together = ('user', 'circle')

    def __str__(self):
        return f"{self.user.username} - {self.circle.name}"