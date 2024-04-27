from rest_framework import permissions


class ArticlePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return obj.author == request.user


class CommentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return obj.author == request.user


class ProfilePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Only retrieve action is allowed.
        if view.action == "retrieve":
            return True
        # List action is allowed only if subscribed query param is present.
        # (The user can see only its subscriptions)
        elif view.action == "list":
            return (
                request.user
                and request.user.is_authenticated
                and request.query_params.get("subscribed") is not None
            )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            # The user can't delete its profile, but can update it.
            return request.method != "DELETE" and obj.user == request.user
