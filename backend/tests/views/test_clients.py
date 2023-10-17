from django.urls import reverse, resolve

from backend.models import Client
from .handler import ViewTestCase


class ClientsViewTestCase(ViewTestCase):
    def test_clients_view_302_for_non_authenticated_users(self):
        response = self.client.get(reverse("clients dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_clients_view_200_for_authenticated_users(self):
        self.client.login(username="user", password="user")
        response = self.client.get(reverse("clients dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_clients_view_matches_with_template(self):
        self.client.login(username="user", password="user")
        response = self.client.get(reverse("clients dashboard"))
        self.assertTemplateUsed(response, "core/pages/clients/dashboard/dashboard.html")

    def test_clients_view_matches_with_urls_view(self):
        func = resolve("/dashboard/clients/").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("/dashboard/clients/", reverse("clients dashboard"))
        self.assertEqual(
            "backend.views.core.clients.dashboard.clients_dashboard", func_name
        )

    def test_clients_view_doesnt_create_invalid_client_no_first_name(self):
        self.client.login(username="user", password="user")
        client_objects_before = Client.objects.count()
        response = self.client.post(
            reverse("clients dashboard"),
            {
                "first_name": "",
                "last_name": "Testy",
            },
        )
        client_objects_after = Client.objects.count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(client_objects_after, client_objects_before)

    def test_clients_view_doesnt_create_invalid_client_no_last_name(self):
        self.client.login(username="user", password="user")
        client_objects_before = Client.objects.count()
        response = self.client.post(
            reverse("clients dashboard"),
            {
                "first_name": "Testy",
                "last_name": "",
            },
        )
        client_objects_after = Client.objects.count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(client_objects_after, client_objects_before)

    # def test_clients_view_doesnt_create_client_valid_details(self):
    #     self.client.login(username="user", password="user")
    #
    #     with self.assertNumQueries(10):
    #         client_objects_before = Client.objects.count()
    #
    #         response = self.client.post(
    #             reverse("clients dashboard"),
    #             {
    #                 "first_name": "firstname",
    #                 "last_name": "lastname",
    #             },
    #         )
    #
    #         client_objects_after = Client.objects.count()
    #         self.assertEqual(response.status_code, 200)
    #         self.assertEqual(
    #             len(response.context["clients"]), client_objects_before + 1
    #         )
    #         self.assertEqual(client_objects_after, client_objects_before + 1)

    def test_clients_check_clients_get_returned(self):
        self.client.login(username="user", password="user")
        headers = {
            "HTTP_HX-request": "true",
        }
        response = self.client.get(reverse("clients dashboard"), **headers)
        amount_of_clients_returned = len(response.context["clients"])
        self.assertEqual(amount_of_clients_returned, 0)
    
        Client.objects.create(
            name="bob smith",
            user=response.wsgi_request.user,
        )
    
        response = self.client.get(reverse("clients dashboard"), **headers)
        amount_of_clients_returned = len(response.context["clients"])
        self.assertEqual(amount_of_clients_returned, 1)

    def test_clients_creating_two_clients(self):
        self.client.login(username="user", password="user")
        headers = {
            "HTTP_HX-request": "true",
        }
        response = self.client.get(reverse("clients dashboard"), **headers)
        amount_of_clients_returned = len(response.context["clients"])
        self.assertEqual(amount_of_clients_returned, 0)
    
        Client.objects.create(
            name="bob smith",
            user=response.wsgi_request.user,
        )

        Client.objects.create(
            name="jane doe",
            user=response.wsgi_request.user,
        )
    
        response = self.client.get(reverse("clients dashboard"), **headers)
        amount_of_clients_returned = len(response.context["clients"])
        self.assertEqual(amount_of_clients_returned, 2)
