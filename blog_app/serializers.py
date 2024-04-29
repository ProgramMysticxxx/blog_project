from blog_app.models import (
    Article,
    ArticleRate,
    Category,
    Comment,
    CommentRate,
    Profile,
    Tag,
    UploadedFile,
    UploadedImage,
)
from rest_framework import serializers
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema_field


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class CategorySerializer(serializers.ModelSerializer):
    articles_count = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    articles_count = serializers.ReadOnlyField()

    class Meta:
        model = Tag
        fields = "__all__"


class ArticleSerializer(serializers.ModelSerializer):
    rating = serializers.ReadOnlyField()
    ratings_count = serializers.ReadOnlyField()
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field="name",
        queryset=Tag.objects.all(),
    )
    cover_url = serializers.ImageField(
        source="cover.image",
        read_only=True,
        allow_null=True,
        required=False,
    )
    author_username = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Article
        fields = "__all__"
        read_only_fields = [
            "author",
            "created_at",
            "updated_at",
        ]


class CommentSerializer(serializers.ModelSerializer):
    rating = serializers.ReadOnlyField()
    ratings_count = serializers.ReadOnlyField()
    author_username = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = [
            "article",
            "author",
            "reply_to",
            "created_at",
            "updated_at",
        ]


class ArticleRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleRate
        fields = "__all__"
        read_only_fields = ["user", "article", "rated_at"]


class CommentRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentRate
        fields = "__all__"
        read_only_fields = ["user", "comment", "rated_at"]


class ProfileSerializer(serializers.ModelSerializer):
    articles_count = serializers.ReadOnlyField()
    subscribers_count = serializers.ReadOnlyField()
    avatar_url = serializers.ImageField(
        source="avatar.image",
        read_only=True,
    )
    total_articles_rating = serializers.ReadOnlyField()

    class Meta:
        model = Profile
        fields = [
            "username",
            "public_name",
            "avatar",
            "avatar_url",
            "bio",
            "articles_count",
            "subscribers_count",
            "total_articles_rating",
        ]
        read_only_fields = ["username"]


class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = "__all__"
        read_only_fields = [
            "user",
            "uploaded_at",
        ]


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = "__all__"
        read_only_fields = [
            "user",
            "uploaded_at",
        ]


class UserTokenSerializer(serializers.Serializer):
    user = UserSerializer()
    token = serializers.CharField()


class UsernamePasswordSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
