from decimal import Decimal
from django.contrib.auth.models import User, Group
from django.test import TestCase
from rest_framework.test import APIClient
from LittleLemonAPI.models import Category, MenuItem, Cart, Order, OrderItem


class LittleLemonAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser("admin_test", "admin@example.com", "TestPass123!")
        self.manager = User.objects.create_user("manager_test", password="TestPass123!")
        self.customer = User.objects.create_user("customer_test", password="TestPass123!")
        self.crew = User.objects.create_user("crew_test", password="TestPass123!")
        Group.objects.get_or_create(name="Manager")[0].user_set.add(self.manager)
        Group.objects.get_or_create(name="Delivery crew")[0].user_set.add(self.crew)
        self.category = Category.objects.create(title="Pasta", slug="pasta")
        self.item = MenuItem.objects.create(title="Tomato Pasta", price=Decimal("5.00"),
                                            category=self.category, featured=False)

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def test_public_menu_items_are_paginated(self):
        response = self.client.get("/api/menu-items/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)

    def test_public_category_list(self):
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["title"], "Pasta")

    def test_admin_can_add_category(self):
        self.auth(self.admin)
        response = self.client.post("/api/categories/", {"title": "Dessert", "slug": "dessert"}, format="json")
        self.assertEqual(response.status_code, 201)

    def test_customer_cannot_add_menu_item(self):
        self.auth(self.customer)
        response = self.client.post("/api/menu-items/", {
            "title": "Soup", "price": "4.00", "category": self.category.id, "featured": False
        }, format="json")
        self.assertEqual(response.status_code, 403)

    def test_manager_can_update_featured_item(self):
        self.auth(self.manager)
        response = self.client.patch(f"/api/menu-items/{self.item.id}/", {"featured": True}, format="json")
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertTrue(self.item.featured)

    def test_admin_can_assign_manager_group(self):
        self.auth(self.admin)
        response = self.client.post("/api/groups/manager/users", {"username": "customer_test"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.customer.groups.filter(name="Manager").exists())

    def test_customer_can_add_and_view_cart(self):
        self.auth(self.customer)
        response = self.client.post("/api/cart/menu-items", {"menuitem": self.item.id, "quantity": 2}, format="json")
        self.assertEqual(response.status_code, 201)
        response = self.client.get("/api/cart/menu-items")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_customer_can_place_order_and_view_own_order(self):
        Cart.objects.create(user=self.customer, menuitem=self.item, quantity=2,
                            unit_price=self.item.price, price=Decimal("10.00"))
        self.auth(self.customer)
        response = self.client.post("/api/orders", {}, format="json")
        self.assertEqual(response.status_code, 201)
        response = self.client.get("/api/orders")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_manager_can_assign_order_to_delivery_crew(self):
        order = Order.objects.create(user=self.customer, total=Decimal("5.00"))
        self.auth(self.manager)
        response = self.client.patch(f"/api/orders/{order.id}", {"delivery_crew": self.crew.id}, format="json")
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.delivery_crew_id, self.crew.id)

    def test_crew_only_sees_assigned_orders_and_can_mark_delivered(self):
        assigned = Order.objects.create(user=self.customer, delivery_crew=self.crew, total=Decimal("5.00"))
        Order.objects.create(user=self.customer, total=Decimal("9.00"))
        self.auth(self.crew)
        response = self.client.get("/api/orders")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        response = self.client.patch(f"/api/orders/{assigned.id}", {"status": True}, format="json")
        self.assertEqual(response.status_code, 200)
        assigned.refresh_from_db()
        self.assertTrue(assigned.status)

    def test_customer_only_sees_own_orders(self):
        Order.objects.create(user=self.customer, total=Decimal("5.00"))
        other = User.objects.create_user("other_customer", password="TestPass123!")
        Order.objects.create(user=other, total=Decimal("9.00"))
        self.auth(self.customer)
        response = self.client.get("/api/orders")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
