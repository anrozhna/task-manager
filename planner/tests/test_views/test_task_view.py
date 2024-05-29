from django.test import TestCase
from django.urls import reverse

from planner.models import TaskType, Task, Worker


class PublicTaskTest(TestCase):
    def test_login_required_task_list(self):
        response = self.client.get(reverse("planner:task-list"))
        self.assertNotEqual(response.status_code, 200)

    def test_login_required_task_detail(self):
        response = self.client.get(reverse(
            "planner:task-detail",
            kwargs={"pk": 1}
        ))
        self.assertNotEqual(response.status_code, 200)

    def test_login_required_task_create(self):
        response = self.client.get((reverse("planner:task-create")))
        self.assertNotEqual(response.status_code, 200)

    def test_login_required_task_update(self):
        response = self.client.get(reverse(
            "planner:task-update",
            kwargs={"pk": 1}
        ))
        self.assertNotEqual(response.status_code, 200)

    def test_login_required_task_delete(self):
        response = self.client.get(reverse(
            "planner:task-delete",
            kwargs={"pk": 1}
        ))
        self.assertNotEqual(response.status_code, 200)


class PrivateTaskTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_tasks = 6
        number_of_assignees = 2
        task_type = TaskType.objects.create(
            name="Test Task Type"
        )

        assignees = []
        for worker_id in range(number_of_assignees):
            assignees.append(Worker.objects.create(
                username=f"Username{worker_id}",
                password="12345"
            ))

        for task_id in range(number_of_tasks):
            task = Task.objects.create(
                name=f"name_{task_id}",
                description="test",
                deadline="2024-05-10T12:00:00Z",
                priority="high",
                task_type=task_type,
            )
            task.assignees.set(assignees)

    def setUp(self):
        self.task = Task.objects.get(id=1)
        self.worker = Worker.objects.get(id=1)
        self.client.force_login(self.worker)

    def test_tasks_list(self):
        response = self.client.get(f"{reverse("planner:task-list")}?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["task_list"]), 1)

    def test_tasks_pagination_is_five(self):
        response = self.client.get(reverse("planner:task-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["task_list"]), 5)

    def test_filter_list_tasks(self):
        response = self.client.get(f"{reverse('planner:task-list')}?name=1")  # noqa Q000
        self.assertEqual(len(response.context["task_list"]), 1)

    def test_task_detail_correct_data(self):
        response = self.client.get(reverse(
            "planner:task-detail",
            kwargs={"pk": self.task.id}
        ))

        self.assertContains(response, self.task.name)
        self.assertContains(response, self.task.description)
        self.assertContains(response, self.task.is_completed)
        self.assertContains(response, self.task.priority)
        self.assertContains(response, self.task.task_type)

    def test_task_create_get(self):
        response = self.client.get(reverse("planner:task-create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Name")
        self.assertContains(response, "Description")
        self.assertContains(response, "Deadline")
        self.assertContains(response, "Task Type")
        self.assertContains(response, "Is completed")
        self.assertContains(response, "Priority")

    def test_task_create_post(self):
        data = {
            "name": "new_task",
            "description": "description",
            "deadline": "2024-05-15T12:00:00Z",
            "is_completed": False,
            "priority": "high",
            "task_type": 1,
            "assignees": [1, 2]
        }
        response = self.client.post(reverse("planner:task-create"), data=data)
        new_task = Task.objects.get(name="new_task")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(new_task.description, data["description"])
        self.assertEqual(new_task.is_completed, data["is_completed"])
        self.assertEqual(new_task.priority, data["priority"])
        self.assertRedirects(
            response, reverse("planner:task-list")
        )

    def test_task_update_get(self):
        response = self.client.get(reverse(
            "planner:task-update",
            kwargs={"pk": self.task.id}
        ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.name)
        self.assertContains(response, self.task.description)
        self.assertContains(response, self.task.priority)
        self.assertContains(response, self.task.task_type)

    def test_task_update_post(self):
        data = {
            "name": self.task.name,
            "description": "description",
            "deadline": "2024-05-15T12:00:00Z",
            "is_completed": True,
            "priority": "low",
            "task_type": 1,
            "assignees": [self.worker.id]
        }
        response = self.client.post(reverse("planner:task-update", kwargs={"pk": self.task.id}), data=data)
        updated_task = Task.objects.get(
            id=self.task.id
        )
        self.assertEqual(updated_task.description, data["description"])
        self.assertEqual(updated_task.is_completed, data["is_completed"])
        self.assertEqual(updated_task.priority, data["priority"])
        self.assertRedirects(
            response, reverse("planner:task-list")
        )

    def test_task_delete_get(self):
        response = self.client.get(reverse(
            "planner:task-delete",
            kwargs={"pk": self.task.id}
        ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f"delete {self.task.name}"
        )

    def test_task_delete_post(self):
        response = self.client.post(reverse(
            "planner:task-delete",
            kwargs={"pk": self.task.id}
        ))
        ls = Task.objects.filter(name=self.task.name)
        self.assertEqual(len(ls), 0)
        self.assertRedirects(
            response, reverse("planner:task-list")
        )

    def test_change_task_is_completed(self):
        task_is_completed_before = Task.objects.get(id=self.task.id).is_completed
        response = self.client.post(reverse(
            "planner:task-done",
            kwargs={"task_id": self.task.id})
        )
        updated_task = Task.objects.get(
            id=self.task.id
        )
        self.assertNotEqual(updated_task.is_completed, task_is_completed_before)
        self.assertRedirects(
            response, reverse("planner:task-list") + "?page=1"
        )
