from django.contrib.auth import get_user_model
from django.test import TestCase

from planner.forms import (
    TaskCreationForm,
    TaskUpdateForm,
    WorkerCreationForm,
    WorkerSearchForm,
    TaskSearchForm,
)
from planner.models import TaskType, Task, Position


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
            "deadline": "2024-06-01T14:00",
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
            deadline="2024-06-01T14:00",
            priority="low",
            task_type=self.task_type,
        )
        task.assignees.add(self.worker)
        form_data = {
            "name": "Updated Task",
            "description": "Updated Description",
            "deadline": "2024-06-01T14:00",
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
            "is_staff": False,
            "is_superuser": False,
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
            deadline="2024-05-10T12:00:00Z",
            priority="high",
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
