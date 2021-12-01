from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrSuperuserOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and obj.owner == request.user or
            request.user.is_superuser
            or obj.user == request.user
        )


class IsProfileOwner(BasePermission):
    """ Only profile owner can change his own info """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj == request.user

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        return obj.user == request.user


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user


class IsMessageSenderOrReceiver(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(obj.sender == request.user or obj.receiver == request.user)


class IsFavoritesOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        return request.user in obj.in_favorites.all()
