from django.urls import path

from planner.views import (
    IndexView,
    register,
    WorkerListView,
    WorkerDetailView,
    WorkerCreateView, WorkerUpdateView, WorkerDeleteView, TaskListView,
)

app_name = "planner"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("register/", register, name='register'),

    path(
        "workers/",
        WorkerListView.as_view(),
        name="worker-list",
    ),
    path(
        "workers/<int:pk>/",
        WorkerDetailView.as_view(),
        name="worker-detail",
    ),
    path(
        "workers/create/",
        WorkerCreateView.as_view(),
        name="worker-create"
    ),
    path(
        "workers/<int:pk>/update/",
        WorkerUpdateView.as_view(),
        name="worker-update",
    ),
    path(
        "workers/<int:pk>/delete/",
        WorkerDeleteView.as_view(),
        name="worker-delete",
    ),

    path(
        "tasks/",
        TaskListView.as_view(),
        name="task-list",
    ),

]
