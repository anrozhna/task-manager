from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect


def index(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return render(request, "planner/index.html")
    else:
        return redirect("login")
