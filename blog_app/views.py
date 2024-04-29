from rest_framework import viewsets, permissions, views, decorators, filters
from blog_app.models import (
    Article,
    ArticleFavorite,
    ArticleRate,
    Category,
    CommentRate,
    Profile,
    ProfileSubscription,
    Tag,
    Comment,
    UploadedFile,
    UploadedImage,
)
from blog_app.permissions import CommentPermission, ArticlePermission, ProfilePermission
from blog_app.serializers import (
    ArticleRateSerializer,
    ArticleSerializer,
    CategorySerializer,
    CommentRateSerializer,
    CommentSerializer,
    ProfileSerializer,
    TagSerializer,
    UploadedFileSerializer,
    UploadedImageSerializer,
    UserTokenSerializer,
    UserSerializer,
    UsernamePasswordSerializer,
)
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    extend_schema_serializer,
    extend_schema_field,
    extend_schema_view,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import parsers
from drf_spectacular.authentication import TokenScheme


@extend_schema(tags=["Auth"])
class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        operation_id="register",
        request=UserSerializer,
        responses=UserTokenSerializer,
    )
    @decorators.action(["POST"], detail=False)
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.get(username=request.data["username"])
        token = Token.objects.create(user=user)
        return Response(
            UserTokenSerializer(
                {
                    "user": user,
                    "token": token,
                }
            ).data,
        )

    @extend_schema(
        operation_id="login",
        request=UsernamePasswordSerializer,
        responses=UserTokenSerializer,
    )
    @decorators.action(["POST"], detail=False)
    def login(self, request):
        request_serializer = UsernamePasswordSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.data

        user = get_object_or_404(User, username=request_data["username"])
        if not user.check_password(request_data["password"]):
            return Response(
                {"error": "Wrong password"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token, _ = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        return Response(
            UserTokenSerializer(
                {
                    "user": serializer.data,
                    "token": token,
                }
            ).data
        )


@extend_schema(tags=["Categories"])
@extend_schema_view(
    list=extend_schema(operation_id="getCategories"),
    retrieve=extend_schema(operation_id="getCategory"),
)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name"]
    ordering_fields = ["name", "articles_count"]


@extend_schema(tags=["Tags"])
@extend_schema_view(
    list=extend_schema(operation_id="getTags"),
    retrieve=extend_schema(operation_id="getTag"),
)
class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name"]
    ordering_fields = ["name", "articles_count"]


@extend_schema(tags=["Articles"])
@extend_schema_view(
    list=extend_schema(
        operation_id="getArticles",
        parameters=[
            OpenApiParameter(
                "favorited",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                "rated",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                "subscribed",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
            ),
        ],
    ),
    retrieve=extend_schema(operation_id="getArticle"),
    create=extend_schema(operation_id="createArticle"),
    update=extend_schema(operation_id="updateArticle"),
    partial_update=extend_schema(operation_id="partialUpdateArticle"),
    destroy=extend_schema(operation_id="deleteArticle"),
)
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    filterset_fields = [
        "created_at",
        "updated_at",
        "author__username",
        "author__id",
        "category__name",
        "tags__name",
    ]
    ordering_fields = [
        "created_at",
        "updated_at",
        "rating",
        "favors__favored_at",
    ]
    search_fields = [
        "title",
        "content",
        "author__username",
        "category__name",
        "tags__name",
    ]
    permission_classes = [ArticlePermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        if (
            self.request.user.is_authenticated
            and self.request.query_params.get("favorited") is not None
        ):
            queryset = queryset.filter(favors__user=self.request.user)
        if (
            self.request.user.is_authenticated
            and self.request.query_params.get("rated") is not None
        ):
            queryset = queryset.filter(rates__user=self.request.user)
        if (
            self.request.user.is_authenticated
            and self.request.query_params.get("subscribed") is not None
        ):
            queryset = queryset.filter(
                author__profile__subscribers__user=self.request.user
            )
        return queryset

    @staticmethod
    def _create_unexistent_tags(tags):
        for tag in tags:
            if not Tag.objects.filter(name=tag).exists():
                Tag.objects.create(name=tag)

    def perform_create(self, serializer):
        for tag in serializer.validated_data["tags"]:
            if not Tag.objects.filter(name=tag).exists():
                Tag.objects.create(name=tag)
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        for tag in serializer.validated_data["tags"]:
            if not Tag.objects.filter(name=tag).exists():
                Tag.objects.create(name=tag)
        return super().perform_update(serializer)

    @extend_schema(operation_id="favoriteArticle", methods=["post"])
    @extend_schema(operation_id="unfavoriteArticle", methods=["delete"])
    @decorators.action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        article = self.get_object()
        user = request.user
        if request.method == "POST":
            ArticleFavorite.objects.update_or_create(user=user, article=article)
            return Response({"detail": "Article added to favorites"})
        elif request.method == "DELETE":
            ArticleFavorite.objects.filter(user=user, article=article).delete()
            return Response({"detail": "Article removed from favorites"})

    @extend_schema(operation_id="rateArticle", methods=["post"])
    @extend_schema(operation_id="unrateArticle", methods=["delete"])
    @decorators.action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def rate(self, request, pk=None):
        article = self.get_object()
        user = request.user
        if request.method == "POST":
            serializer = ArticleRateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, article=article)
            return Response({"detail": "Article rated"})
        elif request.method == "DELETE":
            ArticleRate.objects.filter(user=user, article=article).delete()
            return Response({"detail": "Article un-rated"})


@extend_schema(tags=["Comments"])
@extend_schema_view(
    list=extend_schema(operation_id="getComments"),
    retrieve=extend_schema(operation_id="getComment"),
    create=extend_schema(operation_id="createComment"),
    update=extend_schema(operation_id="updateComment"),
    partial_update=extend_schema(operation_id="partialUpdateComment"),
    destroy=extend_schema(operation_id="deleteComment"),
)
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "article__id",
        "author__id",
        "reply_to__id",
    ]
    permission_classes = [CommentPermission]

    @extend_schema(operation_id="favoriteComment", methods=["post"])
    @extend_schema(operation_id="unfavoriteComment", methods=["delete"])
    @decorators.action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def rate(self, request, pk=None):
        comment = self.get_object()
        user = request.user
        if request.method == "POST":
            serializer = CommentRateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, comment=comment)
            return Response({"detail": "Comment rated"})
        elif request.method == "DELETE":
            CommentRate.objects.filter(user=user, comment=comment).delete()
            return Response({"detail": "Comment un-rated"})


@extend_schema(tags=["Profiles"])
@extend_schema_view(
    list=extend_schema(operation_id="getProfiles"),
    retrieve=extend_schema(operation_id="getProfile"),
    create=extend_schema(operation_id="createProfile"),
    update=extend_schema(operation_id="updateProfile"),
    partial_update=extend_schema(operation_id="partialUpdateProfile"),
    destroy=extend_schema(operation_id="deleteProfile"),
)
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    permission_classes = [ProfilePermission]
    lookup_field = "username"

    def get_queryset(self):
        queryset = super().get_queryset()
        if (
            self.request.user.is_authenticated
            and self.request.query_params.get("subscribed") is not None
        ):
            queryset = queryset.filter(subscribers__user=self.request.user)
        return queryset

    @extend_schema(operation_id="subscribe", methods=["post"])
    @extend_schema(operation_id="unsubscribe", methods=["delete"])
    @decorators.action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, pk=None, **kwargs):
        profile = self.get_object()
        user = request.user

        if profile.user == user:
            return Response(
                {"detail": "You can't subscribe to yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == "POST":
            if not ProfileSubscription.objects.filter(
                user=user, profile=profile
            ).exists():
                ProfileSubscription.objects.create(user=user, profile=profile)
            return Response({"detail": "Profile subscribed"})
        elif request.method == "DELETE":
            ProfileSubscription.objects.filter(user=user, profile=profile).delete()
            return Response({"detail": "Profile un-subscribed"})


@extend_schema(tags=["Images"])
class UploadedImageViewSet(viewsets.ViewSet):
    queryset = UploadedImage.objects.all()
    serializer_class = UploadedImageSerializer
    parser_classes = [parsers.MultiPartParser]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(operation_id="uploadImage")
    def create(self, request):
        serializer = UploadedImageSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)

    @extend_schema(operation_id="getImageInformation")
    def retrieve(self, request, pk=None):
        image = self.get_object()
        serializer = UploadedImageSerializer(
            image,
            context={"request": request},
        )
        return Response(serializer.data)


@extend_schema(tags=["Files"])
class UploadedFileViewSet(viewsets.ViewSet):
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [parsers.MultiPartParser]

    @extend_schema(operation_id="uploadFile")
    def create(self, request):
        serializer = UploadedFileSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)

    @extend_schema(operation_id="getFileInformation")
    def retrieve(self, request, pk=None):
        file = self.get_object()
        serializer = UploadedFileSerializer(
            file,
            context={"request": request},
        )
        return Response(serializer.data)
