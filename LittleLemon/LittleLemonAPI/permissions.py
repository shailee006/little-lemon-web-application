from rest_framework.permissions import BasePermission, SAFE_METHODS

def in_group(user, name):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name=name).exists())

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (request.user.is_authenticated and request.user.is_staff)

class MenuItemPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.method in ("POST", "DELETE"):
            return request.user.is_staff
        # Managers may update menu items (including the item of the day / featured flag).
        return request.user.is_staff or in_group(request.user, "Manager")

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return in_group(request.user, "Manager")

class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return in_group(request.user, "Manager") or (request.user.is_authenticated and request.user.is_staff)
