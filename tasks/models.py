from it_project_task_manager.settings import AUTH_USER_MODEL
from django.contrib.auth.models import AbstractUser
from django.db import models


class TaskType(models.Model):
    name = models.CharField(max_length=63)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=63)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(
        to=Position,
        on_delete=models.CASCADE,
        related_name="worker_position"
    )

    class Meta:
        ordering = ["username", "position"]

    def __str__(self) -> str:
        return f"|Username:{self.username}|" \
               f"full_name:{self.first_name} {self.last_name}|" \
               f"position:{self.position}|" \
               f"email:{self.email}|"


class Task(models.Model):
    class PriorityType(models.TextChoices):
        URGENT = "U", "Urgent"
        HIGH = "H", "High"
        MEDIUM = "M", "Medium"
        LOW = "L", "Low"

    name = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    is_completed = models.BooleanField(verbose_name="task_status")
    priority = models.CharField(max_length=1, choices=PriorityType.choices)
    task_type = models.ForeignKey(to=TaskType, on_delete=models.PROTECT)
    assignees = models.ManyToManyField(to=AUTH_USER_MODEL)

    def __str__(self):
        return f"Priority: {self.priority} Deadline: {self.deadline} Is_Completed: {self.is_completed}"

    class Meta:
        ordering = ["-deadline", "priority"]