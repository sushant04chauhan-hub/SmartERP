from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):

    ROLE_CHOICES = [
        ("ADMIN", "Administrator"),
        ("MANAGER", "Manager"),
        ("HR", "HR"),
        ("INVENTORY", "Inventory"),
        ("PROCUREMENT", "Procurement"),
        ("SALES", "Sales"),
        ("FINANCE", "Finance"),
        ("EMPLOYEE", "Employee"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="EMPLOYEE"
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"