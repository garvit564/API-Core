from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from rest_framework.test import APIClient

from api.models import Product
from django.contrib.auth.models import User


class ProductAPITest(TestCase):

    def setUp(self):

        self.client = APIClient()

        self.user = User.objects.create_user(
            username="rahul",
            password="rahul123"
        )

        self.product = Product.objects.create(
            name="Laptop",
            price=50000,
            discount_price=45000,
            stock=10,
            owner=self.user
        )

    def test_get_products(self):

        response = self.client.get(
            "/api7/products/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_create_product(self):

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            "/api7/products/",
            {
                "name": "Phone",
                "price": 30000,
                "discount_price": 28000,
                "stock": 20
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_login_success(self):

        response = self.client.post(
            "/api7/login/",
            {
                "username": "rahul",
                "password": "rahul123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertIn(
            "access",
            response.data
        )

        self.assertIn(
            "refresh",
            response.data
        )

    def test_login_wrong_password(self):

        response = self.client.post(
            "/api7/login/",
            {
                "username": "rahul",
                "password": "wrongpassword"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            401
        )