import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from planner.forms import (
    TaskCreationForm,
    TaskUpdateForm,
    WorkerCreationForm,
    WorkerSearchForm,
    TaskSearchForm,
)
from planner.models import TaskType, Task, Position


def aware_deadline(*args, **kwargs):
    """Helper to build a timezone-aware deadline for form/model tests."""
    return timezone.make_aware(datetime.datetime(*args, **kwargs))


class TaskFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        TaskType.objects.create(name="Test Task Type")
        get_user_model().objects.create_user(
            username="test_user",
            password="12345",
        )

    def setUp(self):
        self.task_type = TaskType.objects.get(id=1)
        self.worker = get_user_model().objects.get(id=1)

        self.client.force_login(self.worker)

    def test_task_creation_form_valid_data(self):
        form_data = {
            "name": "Test Task",
            "description": "Test Description",
            "deadline": aware_deadline(2024, 6, 1, 14, 0).strftime("%Y-%m-%dT%H:%M"),
            "priority": "low",
            "task_type": self.task_type.id,
            "assignees": [self.worker.id],
        }
        form = TaskCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        task = form.save()
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.description, "Test Description")
        self.assertEqual(task.priority, "low")

    def test_task_creation_form_invalid_data(self):
        form_data = {
            "name": "",
            "description": "Test Description",
            "deadline": "invalid-date",
            "priority": "invalid-priority",
            "task_type": "",
        }
        form = TaskCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("deadline", form.errors)
        self.assertIn("priority", form.errors)
        self.assertIn("task_type", form.errors)

    def test_task_update_form_valid_data(self):
        task = Task.objects.create(
            name="Test Task",
            description="Test Description",
            deadline=aware_deadline(2024, 6, 1, 14, 0),
            priority=Task.Priority.LOW,
            task_type=self.task_type,
        )
        task.assignees.add(self.worker)
        form_data = {
            "name": "Updated Task",
            "description": "Updated Description",
            "deadline": aware_deadline(2024, 6, 1, 14, 0).strftime("%Y-%m-%dT%H:%M"),
            "priority": "high",
            "task_type": self.task_type.id,
            "assignees": [self.worker.id],
        }
        form = TaskUpdateForm(instance=task, data=form_data)
        self.assertTrue(form.is_valid())
        updated_task = form.save()
        self.assertEqual(updated_task.name, "Updated Task")
        self.assertEqual(updated_task.description, "Updated Description")
        self.assertEqual(updated_task.priority, "high")


class WorkerFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        position = Position.objects.create(name="Test Position")
        get_user_model().objects.create_user(
            username="test_user",
            password="12345",
            email="test@example.com",
            position=position,
        )

    def setUp(self):
        self.position = Position.objects.get(id=1)
        self.worker = get_user_model().objects.get(id=1)

        self.client.force_login(self.worker)

    def test_worker_creation_form_valid_data(self):
        form_data = {
            "username": "new_user",
            "password1": "strong_password",
            "password2": "strong_password",
            "first_name": "New",
            "last_name": "User",
            "email": "newuser@example.com",
            "position": self.position,
        }
        form = WorkerCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, "new_user")
        self.assertEqual(user.first_name, "New")
        self.assertEqual(user.last_name, "User")

    def test_worker_creation_form_invalid_data(self):
        form_data = {
            "username": "new_user",
            "password1": "strong_password",
            "password2": "different_password",
            "email": "newuser@example.com",
        }
        form = WorkerCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_worker_creation_form_ignores_privilege_fields(self):
        """Regression test: is_staff/is_superuser must not be settable
        via the public registration form, even if submitted explicitly.
        """
        form_data = {
            "username": "sneaky_user",
            "password1": "strong_password",
            "password2": "strong_password",
            "is_staff": True,
            "is_superuser": True,
        }
        form = WorkerCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)


class WorkerUpdateViewPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(
            username="regular_user",
            password="12345",
        )
        get_user_model().objects.create_user(
            username="other_user",
            password="12345",
        )
        get_user_model().objects.create_user(
            username="staff_user",
            password="12345",
            is_staff=True,
        )

    def test_regular_user_cannot_edit_other_worker(self):
        self.client.login(username="regular_user", password="12345")
        other = get_user_model().objects.get(username="other_user")
        response = self.client.post(
            reverse("planner:worker-update", args=[other.pk]),
            {"username": "hacked", "email": "x@x.com"},
        )
        self.assertEqual(response.status_code, 403)

    def test_regular_user_cannot_self_promote(self):
        self.client.login(username="regular_user", password="12345")
        user = get_user_model().objects.get(username="regular_user")
        response = self.client.post(
            reverse("planner:worker-update", args=[user.pk]),
            {
                "username": "regular_user",
                "email": "x@x.com",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        user.refresh_from_db()
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertRedirects(response, reverse("planner:worker-list"))

    def test_staff_can_edit_any_worker_permissions(self):
        self.client.login(username="staff_user", password="12345")
        other = get_user_model().objects.get(username="other_user")
        response = self.client.post(
            reverse("planner:worker-update", args=[other.pk]),
            {
                "first_name": "Updated",
                "last_name": "Name",
                "email": "x@x.com",
                "is_staff": True,
                "is_superuser": False,
            },
        )
        other.refresh_from_db()
        self.assertTrue(other.is_staff)
        self.assertRedirects(response, reverse("planner:worker-list"))


class SearchFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        task_type = TaskType.objects.create(name="test_task_type")
        position = Position.objects.create(name="test_position")
        worker = get_user_model().objects.create_user(
            username="test_user",
            password="12345",
            email="test@example.com",
            position=position,
        )
        task = Task.objects.create(
            name="test_task",
            description="test",
            deadline=aware_deadline(2024, 5, 10, 12, 0),
            priority=Task.Priority.HIGH,
            task_type=task_type,
        )
        task.assignees.add(worker.id)

    def setUp(self):
        self.task_type = TaskType.objects.get(id=1)
        self.position = Position.objects.get(id=1)
        self.worker = get_user_model().objects.get(id=1)
        self.task = Task.objects.get(id=1)

        self.client.force_login(self.worker)

    def test_worker_search_form_valid_data(self):
        form_data = {"query": "test_user"}
        form = WorkerSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_worker_search_form_empty_data(self):
        form_data = {"query": ""}
        form = WorkerSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_task_search_form_valid_data(self):
        form_data = {"name": "test_task"}
        form = TaskSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_task_search_form_empty_data(self):
        form_data = {"query": ""}
        form = TaskSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_task_type_search_form_valid_data(self):
        form_data = {"name": "test_task_type"}
        form = TaskSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_task_type_search_form_empty_data(self):
        form_data = {"query": ""}
        form = TaskSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_position_search_form_valid_data(self):
        form_data = {"name": "test_position"}
        form = TaskSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_position_search_form_empty_data(self):
        form_data = {"query": ""}
        form = TaskSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
