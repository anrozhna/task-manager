from django.contrib.auth import get_user_model
from django.test import TestCase

from planner.models import TaskType, Position, Task


class TaskTypeModelTest(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(name="test")

    def test_str(self):
        self.assertEqual(str(self.task_type), self.task_type.name)


class PositionModelTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="test")

    def test_str(self):
        self.assertEqual(str(self.position), self.position.name)


class TaskModelTest(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(name="test")

        self.task = Task.objects.create(
            name="test",
            description="test",
            deadline="2024-05-10T12:00:00Z",
            priority="High",
            task_type=self.task_type,
        )

    def test_str(self):
        self.assertEqual(
            str(self.task),
            f"{self.task.name} (priority: {self.task.priority})"
        )


class WorkerModelTest(TestCase):
    username = "test"
    password = "test123"
    first_name = "first"
    last_name = "last"
    position = "position_test"

    def setUp(self):
        self.position = Position.objects.create(name=self.position)
        self.worker = get_user_model().objects.create_user(
            username=self.username,
            password=self.password,
            first_name=self.first_name,
            last_name=self.last_name,
            position=self.position,
        )

    def test_str(self):
        self.assertEqual(
            str(self.worker),
            f"{self.worker.first_name} {self.worker.last_name} "
            f"({self.worker.username})",
        )

    def test_create_with_position(self):
        self.assertEqual(self.worker.username, self.username)
        self.assertTrue(self.worker.check_password(self.password))
        self.assertEqual(self.worker.first_name, self.first_name)
        self.assertEqual(self.worker.last_name, self.last_name)
        self.assertEqual(self.worker.position, self.position)
