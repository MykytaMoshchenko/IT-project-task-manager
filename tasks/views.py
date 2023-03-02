from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST

from .forms import (
    WorkerSearchForm,
    WorkerCreationForm,
    WorkerPositionUpdateForm,
    TaskSearchForm,
    AssigneesForm
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
        sort_by = self.request.GET.get("sort_by", "")
        context["search_form"] = TaskSearchForm(
            initial={"name": name}
        )
        context["sort_by"] = sort_by

        return context

    def get_queryset(self):
        queryset = Task.objects.prefetch_related("assignees")
        name = self.request.GET.get("name")
        sort_by = self.request.GET.get("sort_by")

        if name:
            return queryset.filter(name__icontains=name)

        if sort_by:
            if sort_by == "name":
                queryset = queryset.order_by("name")
            elif sort_by == "deadline":
                queryset = queryset.order_by("deadline")
            elif sort_by == "priority":
                queryset = queryset.order_by("-priority")
            elif sort_by == "completed":
                queryset = queryset.order_by("-is_completed")

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
    fields = [
        "name",
        "description",
        "deadline",
        "priority",
        "task_type",
        "assignees"
    ]
    queryset = Task.objects.prefetch_related("assignees")
    # form_class = TaskCreationForm
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


@method_decorator(require_POST, name='post')
class TaskAssignView(View):
    template_name = "tasks/assign_user.html"

    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        form = AssigneesForm(initial={"assignees": task.assignees.all()})
        return render(request, self.template_name, {"form": form, "task": task})

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        form = AssigneesForm(request.POST)
        if form.is_valid():
            assignees = form.cleaned_data["assignees"]
            task.assignees.set(assignees)
            task.save()
            return redirect("tasks:task-detail", pk=task.id)
        return render(request, self.template_name, {"form": form, "task": task})


class NotificationView(LoginRequiredMixin, View):
    template_name = "tasks/notifications.html"

    def get(self, request):
        user = request.user
        deadline = datetime.now() + timedelta(days=3)
        tasks = Task.objects.prefetch_related(
            "assignees").filter(
            assignees__in=[user],
            deadline__lte=deadline
        ).order_by("deadline")

        context = {
            'tasks': tasks
        }

        return render(request, self.template_name, context)


class TaskUrgentHighView(LoginRequiredMixin, View):
    template_name = "tasks/urgent_high_priority_task_list.html"

    def get(self, request):
        tasks_uh = Task.objects.prefetch_related(
            "assignees"
        ).filter(priority__in=["Urgent", "High"], is_completed=False)

        context = {
            "tasks_uh": tasks_uh
        }
        return render(request, self.template_name, context)


class TaskCompletedView(LoginRequiredMixin, View):
    template_name = "tasks/completed_tasks_list.html"

    def get(self, request):
        tasks_completed = Task.objects.prefetch_related(
            "assignees"
        ).filter(is_completed=True)
        context = {
            "tasks_completed": tasks_completed
        }
        return render(request, self.template_name, context)
