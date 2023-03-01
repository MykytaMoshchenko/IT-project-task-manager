from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import (
    WorkerSearchForm,
    WorkerCreationForm,
    WorkerPositionUpdateForm,
    TaskCreationForm,
    TaskSearchForm
)
from .models import TaskType, Worker, Task, Position


@login_required
def index(request):
    """View function for the home page of the site."""

    logged_worker = request.user
    num_workers = Worker.objects.count()
    num_tasks = Task.objects.count()
    num_tasks_is_solved = Task.objects.filter(is_completed=True).count()
    num_tasks_high_priority = Task.objects.filter(priority="High", is_completed=False).count()
    num_tasks_urgent_priority = Task.objects.filter(priority="Urgent", is_completed=False).count()
    urgent_and_high = num_tasks_high_priority + num_tasks_urgent_priority
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1
    worker_list = Worker.objects.select_related("position")
    current_user_task_list = Task.objects.filter(assignees__in=[request.user.id])

    context = {
        "num_workers": num_workers,
        "num_tasks": num_tasks,
        "num_visits": num_visits + 1,
        "num_tasks_is_solved": num_tasks_is_solved,
        "num_tasks_high_priority":  num_tasks_high_priority,
        "num_tasks_urgent_priority": num_tasks_urgent_priority,
        "urgent_and_high": urgent_and_high,
        "worker_list": worker_list,
        "current_user_task_list": current_user_task_list,
        "logged_worker": logged_worker,
    }

    return render(request, "tasks/index.html", context=context)


class WorkerListView(LoginRequiredMixin, generic.ListView):
    model = Worker
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(WorkerListView, self).get_context_data(**kwargs)
        username = self.request.GET.get("username", "")
        context["search_form"] = WorkerSearchForm(
            initial={"username": username}
        )

        return context

    def get_queryset(self):
        queryset = Worker.objects.select_related("position")
        username = self.request.GET.get("username")

        if username:
            return queryset.filter(username__icontains=username)

        return queryset


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker
    queryset = Worker.objects.select_related("position")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['is_admin'] = user.is_superuser
        return context


class WorkerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Worker
    form_class = WorkerCreationForm


class WorkerPositionUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    form_class = WorkerPositionUpdateForm
    success_url = reverse_lazy("tasks:worker-list")


class WorkerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Worker
    success_url = reverse_lazy("")


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    paginate_by = 8

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = TaskSearchForm(
            initial={"name": name}
        )

        return context

    def get_queryset(self):
        queryset = Task.objects.prefetch_related("assignees")
        name = self.request.GET.get("name")

        if name:
            return queryset.filter(name__icontains=name)

        return queryset


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    queryset = Task.objects.prefetch_related("assignees")

    def is_complete(self):
        task = self.get_object()
        if self.request.method == "POST":
            is_completed = self.request.POST.get("is_completed")
            task.is_completed = is_completed
            task.save()
            return redirect("tasks:task-detail", pk=task.pk)
        return render(self.request, "tasks/task_detail.html", {"task": task})


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    queryset = Task.objects.prefetch_related("assignees")
    form_class = TaskCreationForm
    success_url = reverse_lazy("tasks:tasks-list")


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    # success_url = reverse_lazy("tasks:tasks-list")
    fields = ["is_completed"]

    def get_success_url(self):
        return reverse('tasks:task-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        task = form.save(commit=False)
        is_completed = form.cleaned_data.get('is_completed')
        if is_completed is not None:
            task.is_completed = is_completed
            task.save()
            messages.success(self.request, 'Task status updated successfully.')
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    success_url = reverse_lazy("tasks:tasks-list")