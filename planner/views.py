from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic

from planner.forms import (
    WorkerCreationForm,
    WorkerUpdateForm,
    TaskCreationForm,
    TaskUpdateForm,
    WorkerSearchForm,
    TaskSearchForm,
    PositionSearchForm,
    TaskTypeSearchForm,
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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(WorkerListView, self).get_context_data(**kwargs)
        query = self.request.GET.get("query", "")
        context["search_form"] = WorkerSearchForm(initial={"query": query})
        return context

    def get_queryset(self):
        form = WorkerSearchForm(self.request.GET)
        queryset = (
            get_user_model()
            .objects.all()
            .select_related("position")
            .prefetch_related("tasks")
        )
        if form.is_valid():
            query = form.cleaned_data["query"]
            return queryset.filter(
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
            )
        return queryset


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
    queryset = (
        get_user_model().objects
        .select_related("position")
        .prefetch_related("tasks")
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        worker = get_object_or_404(get_user_model(), pk=self.kwargs["pk"])
        context["completed_tasks"] = worker.tasks.filter(is_completed=True)
        context["incomplete_tasks"] = worker.tasks.filter(is_completed=False)
        return context


class WorkerCreateView(LoginRequiredMixin, generic.CreateView):
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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = TaskSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        form = TaskSearchForm(self.request.GET)
        queryset = (
            Task.objects.all()
            .select_related("task_type")
            .prefetch_related("assignees")
        )
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset


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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PositionListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = PositionSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        form = PositionSearchForm(self.request.GET)
        queryset = Position.objects.all().prefetch_related("workers")
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset


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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TaskTypeListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = TaskTypeSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        form = TaskTypeSearchForm(self.request.GET)
        queryset = TaskType.objects.all().prefetch_related("tasks")
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset


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


class ChangeTaskIsCompletedView(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        task_id = self.kwargs.get("task_id")
        task = get_object_or_404(Task, pk=task_id)
        task.is_completed = not task.is_completed
        task.save()
        full_url = self.request.POST.get("full_url", reverse("planner:task-list"))
        return full_url


class RegisterView(generic.CreateView):
    model = get_user_model()
    form_class = WorkerCreationForm
    template_name = "registration/register.html"

    def form_valid(self, form):
        new_user = form.save()
        return render(
            self.request,
            "registration/register_done.html",
            {"new_user": new_user}
        )


class ToggleAssignToTaskView(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        worker = get_user_model().objects.get(id=self.request.user.id)
        task_id = self.kwargs.get("pk")

        if Task.objects.get(id=task_id) in worker.tasks.all():
            worker.tasks.remove(task_id)
        else:
            worker.tasks.add(task_id)

        page_number = self.request.POST.get("page")
        if page_number:
            return reverse_lazy("planner:task-list") + f"?page={page_number}"
        else:
            return reverse_lazy("planner:task-detail", args=[task_id])
