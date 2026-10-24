from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, MenuItemViewSet, ManagerUsers, DeliveryCrewUsers, CartView, OrderListCreateView, OrderDetailView

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("menu-items", MenuItemViewSet, basename="menuitem")

urlpatterns = [
    path("", include(router.urls)),
    path("groups/manager/users", ManagerUsers.as_view(), name="manager-users"),
    path("groups/delivery-crew/users", DeliveryCrewUsers.as_view(), name="delivery-crew-users"),
    path("cart/menu-items", CartView.as_view(), name="cart"),
    path("orders", OrderListCreateView.as_view(), name="orders"),
    path("orders/<int:pk>", OrderDetailView.as_view(), name="order-detail"),
]
