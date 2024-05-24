from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from planner.models import Task, TaskType


class WorkerCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "email",
            "position",
            "is_staff",
            "is_superuser",
        )
        position = forms.CharField(
            required=False,
        )


class WorkerUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "email",
            "position",
            "is_staff",
            "is_superuser",
        )
        position = forms.CharField(
            required=False,
        )


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Repeat password",
        widget=forms.PasswordInput
    )

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "position",
        )

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password1"] != cd["password2"]:
            raise forms.ValidationError("Passwords don't match.")
        return cd["password2"]


class TaskCreationForm(forms.ModelForm):
    PRIORITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    )
    name = forms.CharField(
        label="Name",
        widget=forms.TextInput(
            attrs={"placeholder": "Enter task name"}
        )
    )
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(
            attrs={
                "placeholder": "Enter task description",
                "rows": 5,
            }
        ),
    )

    deadline = forms.DateTimeField(
        label="Deadline",
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}
        ),
    )

    priority = forms.ChoiceField(
        required=True,
        choices=PRIORITY_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-select"},
        ),
    )

    task_type = forms.ModelChoiceField(
        queryset=TaskType.objects.all(),
        widget=forms.Select(
            attrs={"class": "form-select"},
        ),
        label="",
    )

    assignees = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        label="Assignees",
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )

    class Meta:
        model = Task
        fields = "__all__"


class TaskUpdateForm(TaskCreationForm):
    pass


class WorkerSearchForm(forms.Form):
    query = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search by name / username",
                "aria-label": "Search"
            }
        ),
    )


class TaskSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search by name",
                "aria-label": "Search"
            }
        ),
    )


class PositionSearchForm(TaskSearchForm):
    pass


class TaskTypeSearchForm(TaskSearchForm):
    pass
