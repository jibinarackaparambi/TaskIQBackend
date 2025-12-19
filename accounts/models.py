from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # no username, no extra required fields

    objects = UserManager()

    def __str__(self):
        return self.email

class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "TODO", "To Do"
        INPROGRES = "INPROGRES", "In Progres"
        COMPLETED = "COMPLETED", "Completed"
        PENDING = "PENDING", "Pending"

    title = models.CharField(max_length=30)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)