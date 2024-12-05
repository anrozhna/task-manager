from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from planner.models import Position, Worker


class PublicWorkerTest(TestCase):
    def test_login_required_worker_list(self):
        response = self.client.get(reverse("planner:worker-list"))
        self.assertNotEqual(response.status_code, 200)

    def test_login_required_worker_detail(self):
        response = self.client.get(
            reverse("planner:worker-detail", kwargs={"pk": 1})
        )
        self.assertNotEqual(response.status_code, 200)

    def test_login_required_worker_create(self):
        response = self.client.get((reverse("planner:worker-create")))
        self.assertNotEqual(response.status_code, 200)

    def test_login_required_worker_update(self):
        response = self.client.get(
            reverse("planner:worker-update", kwargs={"pk": 1})
        )
        self.assertNotEqual(response.status_code, 200)

    def test_login_required_worker_delete(self):
        response = self.client.get(
            reverse("planner:worker-delete", kwargs={"pk": 1})
        )
        self.assertNotEqual(response.status_code, 200)


class PrivateWorkerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_workers = 6
        position = Position.objects.create(name="Test Position")
        for driver_id in range(number_of_workers):
            Worker.objects.create(
                username=f"username_{driver_id}",
                password="test_password",
                first_name=f"first_{driver_id}",
                last_name=f"last_{driver_id}",
                position=position,
            )

    def setUp(self):
        self.worker = Worker.objects.get(id=1)
        self.client.force_login(self.worker)

    def test_workers_list(self):
        response = self.client.get(f"{reverse("planner:worker-list")}?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["worker_list"]), 1)

    def test_workers_pagination_is_five(self):
        response = self.client.get(reverse("planner:worker-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["worker_list"]), 5)

    def test_filter_list_workers(self):
        response_username = self.client.get(
            f"{reverse('planner:worker-list')}?query=username_1"
        )  # noqa Q000
        response_first_name = self.client.get(
            f"{reverse('planner:worker-list')}?query=first_1"
        )  # noqa Q000
        response_last_name = self.client.get(
            f"{reverse('planner:worker-list')}?query=last_1"
        )  # noqa Q000
        self.assertEqual(len(response_username.context["worker_list"]), 1)
        self.assertEqual(len(response_first_name.context["worker_list"]), 1)
        self.assertEqual(len(response_last_name.context["worker_list"]), 1)

    def test_worker_detail_correct_data(self):
        response = self.client.get(
            reverse("planner:worker-detail", kwargs={"pk": self.worker.id})
        )
        self.assertContains(response, self.worker.username)
        self.assertContains(response, self.worker.position)

    def test_worker_create_get(self):
        response = self.client.get(reverse("planner:worker-create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First name")
        self.assertContains(response, "Last name")
        self.assertContains(response, "Username")
        self.assertContains(response, "Position")
        self.assertContains(response, "Email")
        self.assertContains(response, "Password")

    def test_worker_create_post(self):
        data = {
            "username": "Username202",
            "password1": "WhatWasThat2024",
            "password2": "WhatWasThat2024",
            "first_name": "First",
            "last_name": "Last",
        }
        response = self.client.post(
            reverse("planner:worker-create"),
            data=data
        )
        new_driver = get_user_model().objects.get(username=data["username"])
        self.assertEqual(new_driver.first_name, data["first_name"])
        self.assertEqual(new_driver.last_name, data["last_name"])
        self.assertRedirects(response, reverse("planner:worker-list"))

    def test_worker_update_get(self):
        response = self.client.get(
            reverse("planner:worker-update", kwargs={"pk": self.worker.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.worker.position)

    def test_worker_update_post(self):
        data = {
            "username": self.worker.username,
            "first_name": "Firstname",
            "last_name": "Lastname",
            "email": "emailunique@gmail.com",
        }
        response = self.client.post(
            reverse(
                "planner:worker-update",
                kwargs={"pk": self.worker.id}),
            data=data
        )
        new_driver = get_user_model().objects.get(id=self.worker.id)
        self.assertEqual(new_driver.first_name, data["first_name"])
        self.assertEqual(new_driver.last_name, data["last_name"])
        self.assertEqual(new_driver.email, data["email"])
        self.assertRedirects(response, reverse("planner:worker-list"))

    def test_worker_delete_get(self):
        response = self.client.get(
            reverse("planner:worker-delete", kwargs={"pk": self.worker.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f"delete {self.worker.first_name} {self.worker.last_name}"
        )

    def test_driver_delete_post(self):
        self.client.post(
            reverse("planner:worker-delete", kwargs={"pk": self.worker.id})
        )
        ls = get_user_model().objects.filter(username=self.worker.username)
        self.assertEqual(len(ls), 0)
