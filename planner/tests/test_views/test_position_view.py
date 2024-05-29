from django.test import TestCase
from django.urls import reverse

from planner.models import Position, Task, Worker


class PublicPositionTest(TestCase):
    def test_login_required_position_list(self):
        response = self.client.get(reverse("planner:position-list"))
        self.assertNotEqual(response.status_code, 200)

    def test_login_required_position_detail(self):
        response = self.client.get(
            reverse("planner:position-detail", kwargs={"pk": 1})
        )
        self.assertNotEqual(response.status_code, 200)

    def test_login_required_position_create(self):
        response = self.client.get((reverse("planner:position-create")))
        self.assertNotEqual(response.status_code, 200)

    def test_login_required_position_update(self):
        response = self.client.get(
            reverse("planner:position-update", kwargs={"pk": 1})
        )
        self.assertNotEqual(response.status_code, 200)

    def test_login_required_position_delete(self):
        response = self.client.get(
            reverse("planner:position-delete", kwargs={"pk": 1})
        )
        self.assertNotEqual(response.status_code, 200)


class PrivatePositionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_positions = 10

        for position_id in range(number_of_positions):
            Position.objects.create(
                name=f"name_{position_id}",
            )

    def setUp(self):
        self.position = Position.objects.get(pk=1)
        self.worker = Worker.objects.create(
            username="Test",
            password="test_123",
            position=self.position,
        )
        self.client.force_login(self.worker)

    def test_position_list(self):
        response = self.client.get(
            f"{reverse("planner:position-list")}?page=2"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["position_list"]), 1)

    def test_position_pagination_is_nine(self):
        response = self.client.get(reverse("planner:position-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["position_list"]), 9)

    def test_filter_list_position(self):
        response = self.client.get(
            f"{reverse('planner:position-list')}?name=1"
        )  # noqa Q000
        self.assertEqual(len(response.context["position_list"]), 1)

    def test_position_detail_correct_data(self):
        response = self.client.get(
            reverse("planner:position-detail", kwargs={"pk": self.position.id})
        )

        self.assertContains(response, self.position.name)

    def test_position_create_get(self):
        response = self.client.get(reverse("planner:position-create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Name")

    def test_position_create_post(self):
        data = {
            "name": "new_position",
        }
        response = self.client.post(
            reverse("planner:position-create"),
            data=data
        )
        new_position = Position.objects.get(name=data["name"])
        self.assertEqual(new_position.name, data["name"])
        self.assertRedirects(response, reverse("planner:position-list"))

    def test_position_update_get(self):
        response = self.client.get(
            reverse("planner:position-update", kwargs={"pk": self.position.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.position.name)

    def test_position_update_post(self):
        data = {
            "name": "updated_name",
        }
        response = self.client.post(
            reverse(
                "planner:position-update",
                kwargs={"pk": self.position.id}
            ),
            data=data,
        )
        updated_position = Position.objects.get(id=self.position.id)
        self.assertEqual(updated_position.name, data["name"])
        self.assertRedirects(response, reverse("planner:position-list"))

    def test_position_delete_get(self):
        response = self.client.get(
            reverse("planner:position-delete", kwargs={"pk": self.position.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"delete {self.position.name}")

    def test_position_delete_post(self):
        self.client.post(
            reverse("planner:position-delete", kwargs={"pk": self.position.id})
        )
        ls = Task.objects.filter(name=self.position.name)
        self.assertEqual(len(ls), 0)
