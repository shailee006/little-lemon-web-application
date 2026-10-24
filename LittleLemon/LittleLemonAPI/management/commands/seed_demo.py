from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from LittleLemonAPI.models import Category, MenuItem

class Command(BaseCommand):
    help = "Create disposable demo users, groups, categories and menu items for local testing."
    def handle(self, *args, **options):
        users = [
            ("admin", "AdminDemo123!", True, None),
            ("manager", "ManagerDemo123!", False, "Manager"),
            ("delivery", "DeliveryDemo123!", False, "Delivery crew"),
            ("customer", "CustomerDemo123!", False, None),
        ]
        for username, password, staff, group_name in users:
            user, created = User.objects.get_or_create(username=username, defaults={"is_staff": staff, "is_superuser": staff})
            if created:
                user.set_password(password)
                user.save()
            else:
                user.is_staff = staff
                user.is_superuser = staff
                user.set_password(password)
                user.save()
            Token.objects.get_or_create(user=user)
            if group_name:
                group, _ = Group.objects.get_or_create(name=group_name)
                group.user_set.add(user)
        category_data = [("Pasta", "pasta"), ("Main Course", "main-course"), ("Dessert", "dessert")]
        categories = {}
        for title, slug in category_data:
            categories[slug], _ = Category.objects.get_or_create(slug=slug, defaults={"title": title})
        items = [
            ("Beef Pasta", "12.00", "pasta", True),
            ("Tomato Pasta", "5.00", "pasta", False),
            ("Grilled Chicken", "15.00", "main-course", True),
            ("Lemon Cake", "6.50", "dessert", False),
            ("Garden Salad", "7.25", "main-course", False),
            ("Mushroom Pasta", "10.00", "pasta", False),
            ("Chocolate Tart", "8.00", "dessert", True),
        ]
        for title, price, slug, featured in items:
            MenuItem.objects.get_or_create(title=title, defaults={"price": Decimal(price), "category": categories[slug], "featured": featured})
        self.stdout.write(self.style.SUCCESS("Demo data created. See notes.txt for disposable credentials."))
