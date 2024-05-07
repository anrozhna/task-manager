from django.urls import path

from planner.views import (
    index,
)

app_name = "planner"

urlpatterns = [
    path("", index, name="index")
]
