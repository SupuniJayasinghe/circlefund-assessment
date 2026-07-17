from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP

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
    
class Round(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("PENDING", "Pending Approval"),
        ("CLOSED", "Closed"),
    ]

    circle = models.ForeignKey(Circle, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    contribution_amount = models.IntegerField(default=5000)  # minor units
    penalty_rate = models.IntegerField(default=3)
    deadline = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True)


class Contribution(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name="contributions")
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    penalty = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("round", "member")