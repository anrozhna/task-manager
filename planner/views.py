from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from planner.forms import (
    WorkerCreationForm,
    UserRegistrationForm
)
from planner.models import Task


class IndexView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = "planner/index.html"
    paginate_by = 5
    queryset = Task.objects.prefetch_related("assignees")


class WorkerListView(LoginRequiredMixin, generic.ListView):
    model = get_user_model()
    paginate_by = 5


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
    queryset = get_user_model().objects.select_related("position")


class WorkerCreateView(generic.edit.CreateView):
    model = get_user_model()
    form_class = WorkerCreationForm
    success_url = reverse_lazy("planner:index")


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
