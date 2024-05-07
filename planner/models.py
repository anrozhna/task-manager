from django.contrib.auth.models import AbstractUser
from django.db import models


class TaskType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("top", "Top"),
    )

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    deadline = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=255, choices=PRIORITY_CHOICES)
    task_type = models.ForeignKey(
        TaskType, related_name="tasks", on_delete=models.CASCADE
    )
    assignees = models.ManyToManyField("Worker", related_name="tasks")

    def __str__(self):
        return f"{self.name} (priority: {self.priority})"


class Worker(AbstractUser):
    position = models.ForeignKey(
        Position,
        related_name="workers",
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
