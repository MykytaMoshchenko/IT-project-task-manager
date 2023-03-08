from django.urls import reverse

from it_project_task_manager.settings import AUTH_USER_MODEL
from django.contrib.auth.models import AbstractUser
from django.db import models


class TaskType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(
        to=Position,
        on_delete=models.RESTRICT,
        related_name="worker_position",
        null=True
    )

    class Meta:
        ordering = ["username", "position"]

    def __str__(self) -> str:
        return (f"username: {self.username} |" +
                f" full_name: {self.first_name} {self.last_name} |" +
                f" position: {self.position}")

    def get_absolute_url(self):
        return reverse("tasks:worker-detail", kwargs={"pk": self.pk})


class Task(models.Model):
    class PriorityType(models.TextChoices):
        URGENT = "Urgent", "Urgent"
        HIGH = "High", "High"
        MEDIUM = "Medium", "Medium"
        LOW = "Low", "Low"

    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255)
    deadline = models.DateField()
    is_completed = models.BooleanField(verbose_name="task_status", default=False)
    priority = models.CharField(max_length=6, choices=PriorityType.choices)
    task_type = models.ForeignKey(to=TaskType, on_delete=models.PROTECT)
    assignees = models.ManyToManyField(to=AUTH_USER_MODEL)

    def __str__(self):
        return f"{self.name} -  {self.priority} priority, Deadline: {self.deadline} Is_Completed: {self.is_completed}"

    class Meta:
        ordering = ["deadline", "priority"]
