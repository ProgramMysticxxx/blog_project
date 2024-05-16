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

class ProfileSerializer(serializers.ModelSerializer):
    articles_count = serializers.ReadOnlyField()
    subscribers_count = serializers.ReadOnlyField()
    avatar_url = serializers.ImageField(
        source="avatar.image",
        read_only=True,
    )
    total_articles_rating = serializers.ReadOnlyField()
    date_joined = serializers.ReadOnlyField(source="user.date_joined")
    is_staff = serializers.ReadOnlyField(source="user.is_staff")
    is_you = serializers.SerializerMethodField()

    def get_is_you(self, obj) -> bool:
        request = self.context.get("request")
        return request.user == obj.user

    are_you_subscribed = serializers.SerializerMethodField()

    def get_are_you_subscribed(self, obj) -> bool:
        request = self.context.get("request")
        if request.user.is_authenticated:
            return obj.subscribers.filter(user=request.user).exists()
        return False

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
            "date_joined",
            "is_staff",
            "is_you",
            "are_you_subscribed",
        ]
        read_only_fields = ["username"]

class ArticleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
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
    # author_username = serializers.ReadOnlyField(source="author.username")
    # author_avatar_url = serializers.ImageField(
    #     source="author.profile.avatar.image",
    #     read_only=True,
    # )
    # author_date_joined = serializers.ReadOnlyField(source="author.date_joined")
    # author_bio = serializers.ReadOnlyField(source="author.profile.bio")
    # author_public_name = serializers.ReadOnlyField(source="author.profile.public_name")
    # author_rating = serializers.ReadOnlyField(source="author.profile.rating")
    # author_subscribers_count = serializers.ReadOnlyField(source="author.profile.subscribers_count")
    author_details = ProfileSerializer(source="author.profile")

    your_rate = serializers.SerializerMethodField()
    you_author = serializers.SerializerMethodField()

    # FIXME temporary solution
    def to_internal_value(self, data):
        for tag in data.get("tags"):
            if not Tag.objects.filter(name=tag).exists():
                Tag.objects.create(name=tag)
        return super().to_internal_value(data)

    def get_your_rate(self, obj) -> bool | None:
        user = self.context.get("request").user
        if user.is_authenticated:
            rate = obj.article_rates.filter(user=user).first()
            if rate:
                return rate.is_positive
        return None

    def get_you_author(self, obj) -> bool | None:
        user = self.context.get("request").user
        if user.is_authenticated:
            return obj.author == user
        return None

    is_your_bookmark = serializers.SerializerMethodField()

    def get_is_your_bookmark(self, obj) -> bool | None:
        user = self.context.get("request").user
        if user.is_authenticated:
            return obj.favors.filter(user=user).exists()
        return None

    class Meta:
        model = Article
        fields = "__all__"
        read_only_fields = [
            "author",
            "created_at",
            "updated_at",
        ]


class CommentSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    ratings_count = serializers.ReadOnlyField()
    # author_username = serializers.ReadOnlyField(source="author.username")
    # author_avatar_url = serializers.ImageField(
    #     source="author.profile.avatar.image",
    #     read_only=True,
    # )
    author_details = ProfileSerializer(source="author.profile")
    is_your_comment = serializers.SerializerMethodField()

    def get_is_your_comment(self, obj) -> bool | None:
        user = self.context.get("request").user
        return obj.author == user

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = [
            "author",
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
