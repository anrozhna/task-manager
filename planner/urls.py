from django.urls import path

from planner.views import (
    IndexView,
    WorkerListView,
    WorkerDetailView
)

app_name = "planner"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),

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
