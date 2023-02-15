from django.urls import path

from tasks.views import index

urlpatterns = [
    path("", index, name="index"),
    ]

app_name = "tasks"
