from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic

from planner.forms import (
    WorkerCreationForm,
    WorkerUpdateForm,
    UserRegistrationForm, TaskCreationForm, TaskUpdateForm
)
from planner.models import Task, Position, TaskType


class IndexView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = "planner/index.html"
    paginate_by = 5
    queryset = Task.objects.prefetch_related("assignees")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        num_tasks = Task.objects.count()
        num_workers = get_user_model().objects.count()
        num_positions = Position.objects.count()
        num_visits = self.request.session.get("num_visits", 0)
        self.request.session["num_visits"] = num_visits + 1

        context["num_tasks"] = num_tasks
        context["num_workers"] = num_workers
        context["num_positions"] = num_positions
        context["num_visits"] = num_visits + 1

        return context


class WorkerListView(LoginRequiredMixin, generic.ListView):
    model = get_user_model()
    paginate_by = 5


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
    queryset = get_user_model().objects.select_related("position")


class WorkerCreateView(generic.CreateView):
    model = get_user_model()
    form_class = WorkerCreationForm
    success_url = reverse_lazy("planner:worker-list")


class WorkerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = get_user_model()
    form_class = WorkerUpdateForm
    template_name = "planner/worker_form.html"
    success_url = reverse_lazy("planner:worker-list")


class WorkerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = get_user_model()
    success_url = reverse_lazy("planner:worker-list")


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    paginate_by = 5


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    queryset = Task.objects.prefetch_related("assignees")


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskCreationForm
    success_url = reverse_lazy("planner:task-list")


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskUpdateForm
    template_name = "planner/task_form.html"
    success_url = reverse_lazy("planner:task-list")


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    success_url = reverse_lazy("planner:task-list")


class PositionListView(LoginRequiredMixin, generic.ListView):
    model = Position
    paginate_by = 9


class PositionDetailView(LoginRequiredMixin, generic.DetailView):
    model = Position
    queryset = Position.objects.prefetch_related("workers")


class PositionCreateView(LoginRequiredMixin, generic.CreateView):
    model = Position
    fields = "__all__"
    success_url = reverse_lazy("planner:position-list")


class PositionUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Position
    fields = "__all__"
    template_name = "planner/position_form.html"
    success_url = reverse_lazy("planner:position-list")


class PositionDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Position
    success_url = reverse_lazy("planner:position-list")


class TaskTypeListView(LoginRequiredMixin, generic.ListView):
    model = TaskType
    paginate_by = 9
    template_name = "planner/task_type_list.html"
    context_object_name = "task_type_list"


class TaskTypeDetailView(LoginRequiredMixin, generic.DetailView):
    model = TaskType
    queryset = TaskType.objects.prefetch_related("tasks")
    template_name = "planner/task_type_detail.html"
    context_object_name = "task_type"


class TaskTypeCreateView(LoginRequiredMixin, generic.CreateView):
    model = TaskType
    fields = "__all__"
    success_url = reverse_lazy("planner:task-type-list")
    template_name = "planner/task_type_form.html"
    context_object_name = "task_type"


class TaskTypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = TaskType
    fields = "__all__"
    success_url = reverse_lazy("planner:task-type-list")
    template_name = "planner/task_type_form.html"
    context_object_name = "task_type"


class TaskTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = TaskType
    template_name = "planner/task_type_confirm_delete.html"
    context_object_name = "task_type"
    success_url = reverse_lazy("planner:task-type-list")


@login_required
def change_task_is_completed(request, task_id):
    if request.method == "POST":
        task = get_object_or_404(Task, pk=task_id)
        task.is_completed = not task.is_completed
        task.save()
        page_number = request.POST.get("page", 1)
        return redirect(f"{reverse("planner:task-list")}?page={page_number}")
    else:
        return HttpResponseNotAllowed(["POST"])


def register(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data["password1"])
            new_user.save()
            return render(
                request,
                "registration/register_done.html",
                {"new_user": new_user}
            )
    else:
        user_form = UserRegistrationForm()
    return render(
        request,
        "registration/register.html",
        {"form": user_form}
    )
