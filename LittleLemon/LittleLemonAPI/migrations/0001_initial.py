from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, unique=True)),
                ("slug", models.SlugField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="MenuItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("price", models.DecimalField(decimal_places=2, max_digits=6)),
                ("featured", models.BooleanField(default=False)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="menu_items", to="LittleLemonAPI.category")),
            ],
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.BooleanField(choices=[(False, "Pending"), (True, "Delivered")], default=False)),
                ("total", models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ("date", models.DateTimeField(auto_now_add=True)),
                ("delivery_crew", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="delivery_orders", to=settings.AUTH_USER_MODEL)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="customer_orders", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Cart",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveSmallIntegerField(default=1)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=6)),
                ("price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("menuitem", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="LittleLemonAPI.menuitem")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="cart_items", to=settings.AUTH_USER_MODEL)),
            ],
            options={"unique_together": {("user", "menuitem")}},
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveSmallIntegerField()),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=6)),
                ("price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("menuitem", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="LittleLemonAPI.menuitem")),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="LittleLemonAPI.order")),
            ],
        ),
    ]
