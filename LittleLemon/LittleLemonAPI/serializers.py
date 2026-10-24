from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title", "slug"]

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "category", "featured"]

class CartSerializer(serializers.ModelSerializer):
    menuitem_title = serializers.CharField(source="menuitem.title", read_only=True)
    class Meta:
        model = Cart
        fields = ["id", "menuitem", "menuitem_title", "quantity", "unit_price", "price"]
        read_only_fields = ["unit_price", "price"]

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem_title = serializers.CharField(source="menuitem.title", read_only=True)
    class Meta:
        model = OrderItem
        fields = ["menuitem", "menuitem_title", "quantity", "unit_price", "price"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = serializers.CharField(source="user.username", read_only=True)
    delivery_crew_name = serializers.CharField(source="delivery_crew.username", read_only=True)
    class Meta:
        model = Order
        fields = ["id", "customer", "delivery_crew", "delivery_crew_name", "status", "total", "date", "items"]
        read_only_fields = ["customer", "delivery_crew", "total", "date", "items", "delivery_crew_name"]

class ManagerUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    def validate_username(self, value):
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username does not exist.")
        return value
