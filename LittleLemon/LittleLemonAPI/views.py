from decimal import Decimal
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, viewsets, filters
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Category, MenuItem, Cart, Order, OrderItem
from .permissions import IsAdminOrReadOnly, MenuItemPermission, IsManager, IsManagerOrAdmin, in_group
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, ManagerUserSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("id")
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.select_related("category").all().order_by("id")
    serializer_class = MenuItemSerializer
    permission_classes = [MenuItemPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["category", "featured"]
    ordering_fields = ["price", "title"]
    ordering = ["id"]

    def partial_update(self, request, *args, **kwargs):
        if not (request.user.is_staff or in_group(request.user, "Manager")):
            return Response({"detail": "Only admins or managers can update menu items."}, status=403)
        return super().partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not (request.user.is_staff or in_group(request.user, "Manager")):
            return Response({"detail": "Only admins or managers can update menu items."}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"detail": "Only admins can delete menu items."}, status=403)
        return super().destroy(request, *args, **kwargs)

class GroupUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    group_name = None
    def get(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Admin access required."}, status=403)
        group, _ = Group.objects.get_or_create(name=self.group_name)
        return Response([{"id": u.id, "username": u.username} for u in group.user_set.all()])
    def post(self, request):
        if self.group_name == "Manager":
            allowed = request.user.is_staff
        else:
            allowed = request.user.is_staff or in_group(request.user, "Manager")
        if not allowed:
            return Response({"detail": "Insufficient permissions."}, status=403)
        serializer = ManagerUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(username=serializer.validated_data["username"])
        group, _ = Group.objects.get_or_create(name=self.group_name)
        group.user_set.add(user)
        return Response({"message": f"user added to the {self.group_name.lower()} group"}, status=200)
    def delete(self, request):
        if not (request.user.is_staff or in_group(request.user, "Manager")):
            return Response({"detail": "Insufficient permissions."}, status=403)
        username = request.data.get("username")
        user = get_object_or_404(User, username=username)
        group, _ = Group.objects.get_or_create(name=self.group_name)
        group.user_set.remove(user)
        return Response(status=204)

class ManagerUsers(GroupUsersView):
    group_name = "Manager"
class DeliveryCrewUsers(GroupUsersView):
    group_name = "Delivery crew"

class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response(CartSerializer(Cart.objects.filter(user=request.user).select_related("menuitem"), many=True).data)
    def post(self, request):
        item = get_object_or_404(MenuItem, pk=request.data.get("menuitem"))
        try:
            quantity = int(request.data.get("quantity", 1))
            if quantity < 1: raise ValueError()
        except (TypeError, ValueError):
            return Response({"quantity": "Must be a positive integer."}, status=400)
        cart, created = Cart.objects.get_or_create(
            user=request.user, menuitem=item,
            defaults={"quantity": quantity, "unit_price": item.price, "price": item.price * quantity}
        )
        if not created:
            cart.quantity += quantity
            cart.price = cart.unit_price * cart.quantity
            cart.save()
        return Response(CartSerializer(cart).data, status=201 if created else 200)
    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=204)

class OrderListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        if request.user.is_staff or in_group(request.user, "Manager"):
            orders = Order.objects.all()
        elif in_group(request.user, "Delivery crew"):
            orders = Order.objects.filter(delivery_crew=request.user)
        else:
            orders = Order.objects.filter(user=request.user)
        return Response(OrderSerializer(orders.prefetch_related("items__menuitem"), many=True).data)
    @transaction.atomic
    def post(self, request):
        cart_items = list(Cart.objects.filter(user=request.user).select_related("menuitem"))
        if not cart_items:
            return Response({"detail": "Your cart is empty."}, status=400)
        total = sum((item.price for item in cart_items), Decimal("0.00"))
        order = Order.objects.create(user=request.user, total=total)
        for item in cart_items:
            OrderItem.objects.create(order=order, menuitem=item.menuitem, quantity=item.quantity,
                                     unit_price=item.unit_price, price=item.price)
        Cart.objects.filter(user=request.user).delete()
        return Response(OrderSerializer(order).data, status=201)

class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        if in_group(request.user, "Delivery crew"):
            if order.delivery_crew_id != request.user.id:
                return Response({"detail": "This order is not assigned to you."}, status=403)
            if "status" in request.data:
                value = request.data["status"]
                if not isinstance(value, bool):
                    return Response({"status": "Must be true or false."}, status=400)
                order.status = value
            order.save()
            return Response(OrderSerializer(order).data)
        if request.user.is_staff or in_group(request.user, "Manager"):
            if "delivery_crew" in request.data:
                crew = get_object_or_404(User, pk=request.data["delivery_crew"])
                if not in_group(crew, "Delivery crew"):
                    return Response({"detail": "Selected user is not in the Delivery crew group."}, status=400)
                order.delivery_crew = crew
            if "status" in request.data:
                value = request.data["status"]
                if not isinstance(value, bool):
                    return Response({"status": "Must be true or false."}, status=400)
                order.status = value
            order.save()
            return Response(OrderSerializer(order).data)
        return Response({"detail": "Insufficient permissions."}, status=403)
    def delete(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        if not (request.user.is_staff or in_group(request.user, "Manager")):
            return Response({"detail": "Only admins or managers can delete orders."}, status=403)
        order.delete()
        return Response(status=204)
