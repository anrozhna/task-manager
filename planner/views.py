from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

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
