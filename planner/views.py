from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic

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
