from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from clubs.factory import ClubFactory
from clubs.models import Club
from courts.models import Court
from users.models import CustomUser

UserModel = get_user_model()


class TestClubsAPIViews(APITestCase):
    def setUp(self) -> None:
        self.user = UserModel.objects.create_superuser(
            email="<EMAIL>", password="<PASSWORD>"
        )
        self.club = ClubFactory.create()
        self.club.employees.add(self.user)
        self.club.save()
        self.client = APIClient()

    def test_list_clubs_returns_clubs(self):
        self.client.login(username=self.user.email, password=self.user.password)
        response: Response = self.client.get(reverse("clubs-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], "Test")
        self.assertEqual(len(response.data), 1)

    def test_get_club_returns_club_details(self):
        self.client.login(username=self.user.email, password=self.user.password)
        response: Response = self.client.get(
            reverse("clubs-detail", kwargs={"pk": self.club.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test")

    def test_get_club_courts_returns_courts(self):
        court: Court = Court.objects.create(
            name="test",
            club_id=self.club,
            is_indoor=False,
            is_lit=False,
            sport_type="Tennis",
            surface_type="Clay",
        )
        court.refresh_from_db()
        self.client.force_authenticate(self.user)
        response: Response = self.client.get(
            reverse("clubs-get-club-courts", kwargs={"pk": self.club.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["club_id"], self.club.id)
        self.assertEqual(len(response.data), 1)

    def test_get_club_employees_with_admin_returns_employees_list(self):
        self.client.force_authenticate(self.user)
        response: Response = self.client.get(
            reverse("clubs-get-club-employees", kwargs={"pk": self.club.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0],
            {"first_name": self.user.first_name, "last_name": self.user.last_name},
        )

    def test_get_club_employees_with_employee_returns_employees_list(self):
        new_user: CustomUser = CustomUser.objects.create(
            email="<EMAIL2>", password="<PASSWORD>"
        )
        self.club.employees.add(new_user)
        self.client.force_authenticate(new_user)
        response: Response = self.client.get(
            reverse("clubs-get-club-employees", kwargs={"pk": self.club.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_club_employees_unauthorized_user_returns_error(self):
        new_user: CustomUser = CustomUser.objects.create(
            email="<EMAIL2>", password="<PASSWORD>"
        )
        self.client.force_authenticate(new_user)
        response: Response = self.client.get(
            reverse("clubs-get-club-employees", kwargs={"pk": self.club.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
