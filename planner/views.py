from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic

from planner.models import Task


def index(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        tasks = Task.objects.filter(assignees=request.user)
        context = {
            "tasks": tasks
        }
        return render(request, "planner/index.html", context=context)
    else:
        return redirect("login")


class WorkerListView(generic.ListView):
    model = get_user_model()
    paginate_by = 10


class WorkerDetailView(generic.DetailView):
    model = get_user_model()
    queryset = get_user_model().objects.select_related("position")
