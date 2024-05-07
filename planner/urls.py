from django.urls import path

from planner.views import (
    index,
    WorkerListView,
    WorkerDetailView
)

app_name = "planner"

urlpatterns = [
    path("", index, name="index"),

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
]
