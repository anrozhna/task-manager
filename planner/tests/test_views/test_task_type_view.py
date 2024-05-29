from django.test import TestCase
from django.urls import reverse

from planner.models import TaskType, Task, Worker


class PublicTaskTypeTest(TestCase):
    def test_login_required_task_type_list(self):
        response = self.client.get(reverse("planner:task-type-list"))
        self.assertNotEqual(response.status_code, 200)

    def test_login_required_task_type_detail(self):
        response = self.client.get(reverse(
            "planner:task-type-detail",
            kwargs={"pk": 1}
        ))
        self.assertNotEqual(response.status_code, 200)

    def test_login_required_task_type_create(self):
        response = self.client.get((reverse("planner:task-type-create")))
        self.assertNotEqual(response.status_code, 200)

    def test_login_required_task_type_update(self):
        response = self.client.get(reverse(
            "planner:task-type-update",
            kwargs={"pk": 1}
        ))
        self.assertNotEqual(response.status_code, 200)

    def test_login_required_task_type_delete(self):
        response = self.client.get(reverse(
            "planner:task-type-delete",
            kwargs={"pk": 1}
        ))
        self.assertNotEqual(response.status_code, 200)


class PrivateTaskTypeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_task_types = 10

        for task_type_id in range(number_of_task_types):
            TaskType.objects.create(
                name=f"name_{task_type_id}",
            )

    def setUp(self):
        self.task_type = TaskType.objects.get(pk=1)
        self.worker = Worker.objects.create(
            username="Test",
            password="test_123",
        )
        self.client.force_login(self.worker)

    def test_task_types_list(self):
        response = self.client.get(f"{reverse("planner:task-type-list")}?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["task_type_list"]), 1)

    def test_task_types_pagination_is_nine(self):
        response = self.client.get(reverse("planner:task-type-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["task_type_list"]), 9)

    def test_filter_list_task_types(self):
        response = self.client.get(f"{reverse('planner:task-type-list')}?name=1")  # noqa Q000
        self.assertEqual(len(response.context["task_type_list"]), 1)

    def test_task_type_detail_correct_data(self):
        response = self.client.get(reverse(
            "planner:task-type-detail",
            kwargs={"pk": self.task_type.id}
        ))

        self.assertContains(response, self.task_type.name)

    def test_task_type_create_get(self):
        response = self.client.get(reverse("planner:task-type-create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Name")

    def test_task_type_create_post(self):
        data = {
            "name": "new_task_type",
        }
        response = self.client.post(reverse("planner:task-type-create"), data=data)
        new_task_type = TaskType.objects.get(name=data["name"])
        self.assertEqual(new_task_type.name, data["name"])
        self.assertRedirects(
            response, reverse("planner:task-type-list")
        )

    def test_task_type_update_get(self):
        response = self.client.get(reverse(
            "planner:task-type-update",
            kwargs={"pk": self.task_type.id}
        ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task_type.name)

    def test_task_type_update_post(self):
        data = {
            "name": "updated_name",
        }
        response = self.client.post(reverse(
            "planner:task-type-update",
            kwargs={"pk": self.task_type.id}
        ), data=data)
        updated_task_type = TaskType.objects.get(
            id=self.task_type.id
        )
        self.assertEqual(updated_task_type.name, data["name"])
        self.assertRedirects(
            response, reverse("planner:task-type-list")
        )

    def test_task_type_delete_get(self):
        response = self.client.get(reverse(
            "planner:task-type-delete",
            kwargs={"pk": self.task_type.id}
        ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f"delete {self.task_type.name}"
        )

    def test_task_type_delete_post(self):
        self.client.post(reverse(
            "planner:task-type-delete",
            kwargs={"pk": self.task_type.id}
        ))
        ls = Task.objects.filter(name=self.task_type.name)
        self.assertEqual(len(ls), 0)
