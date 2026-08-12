from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class TaskType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class TaskQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_completed=False)

    def completed(self):
        return self.filter(is_completed=True)

    def overdue(self):
        return self.filter(is_completed=False, deadline__lt=timezone.now())

    def for_worker(self, worker):
        return self.filter(assignees=worker)


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    name = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=Priority.choices)
    task_type = models.ForeignKey(
        TaskType, related_name="tasks", on_delete=models.PROTECT
    )
    assignees = models.ManyToManyField("Worker", related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TaskQuerySet.as_manager()

    class Meta:
        ordering = ["deadline"]
        indexes = [
            models.Index(fields=["is_completed", "deadline"]),
            models.Index(fields=["priority"]),
        ]

    @property
    def is_overdue(self) -> bool:
        return not self.is_completed and self.deadline < timezone.now()

    def __str__(self):
        return f"{self.name} (priority: {self.priority})"


class Worker(AbstractUser):
    position = models.ForeignKey(
        Position,
        related_name="workers",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ["username"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
