from django.conf import settings
from django.urls import include, path
from rest_framework import routers
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from blog_app import views
from blog_app.views import ArticleViewSet, CategoryViewSet, TagViewSet

router = routers.DefaultRouter()
router.register("auth", views.AuthViewSet, basename="auth")
router.register("categories", CategoryViewSet)
router.register("tags", TagViewSet)
router.register("articles", ArticleViewSet)
router.register("comments", views.CommentViewSet)
router.register("profiles", views.ProfileViewSet)
router.register("uploaded_images", views.UploadedImageViewSet)
router.register("uploaded_files", views.UploadedFileViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
