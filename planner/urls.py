from django.urls import path

from planner.views import (
    IndexView,
    register,
    WorkerListView,
    WorkerDetailView,
    WorkerCreateView,
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

]
