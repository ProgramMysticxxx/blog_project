from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.db.models import Sum, Count

from blog_app.models import (
    Article,
    ArticleFavorite,
    ArticleRate,
    Category,
    CommentRate,
    Profile,
    ProfileSubscription,
    Tag,
    UploadedFile,
    UploadedImage,
    Comment,
)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "category",
        "author",
        "editor_choice",
        "rating",
        "comments",
        "tags_list",
        "created_at",
        "updated_at",
    )

    ordering = ("-updated_at",)

    date_hierarchy = "created_at"

    list_filter = ("author", "category", "tags", "editor_choice")

    search_fields = [
        "title",
        "content",
        "author__username",
        "category__name",
        "tags__name",
    ]

    @admin.display(ordering="rating")
    def rating(self, obj):
        return obj.rating

    @admin.display(ordering="comments__count")
    def comments(self, obj):
        return obj.comments.count()

    def tags_list(self, obj):
        return [str(tag) for tag in obj.tags.all()]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "articles", "rating")

    search_fields = ["name"]

    def articles(self, obj):
        return obj.articles.count()

    def rating(self, obj):
        return obj.articles.aggregate(Sum("rating"))["rating__sum"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "articles_count")

    search_fields = ["name"]

    def articles_count(self, obj):
        return obj.articles.count()


@admin.register(ArticleRate)
class ArticleRateAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "is_positive")

    search_fields = ["article__title", "user__username"]

    list_filter = ("user", "article")

    def article(self, obj):
        return obj.article.title


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "content",
        "article",
        "author",
        "replies",
        "reply_to",
        "created_at",
        "updated_at",
    )

    search_fields = [
        "content",
        "article__title",
        "author__username",
    ]

    list_filter = (
        "author",
        "article",
        "reply_to",
    )

    date_hierarchy = "updated_at"

    def article(self, obj):
        return obj.article.title

    def replies(self, obj):
        return obj.replies.count()


@admin.register(CommentRate)
class CommentRateAdmin(admin.ModelAdmin):
    list_display = ("comment", "user", "is_positive")

    search_fields = ["comment__content", "user__username"]

    list_filter = ("user", "comment")

    def comment(self, obj):
        return obj.comment.content


@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image",
        "user",
        "uploaded_at",
    )

    list_filter = ("user",)

    search_fields = ["user__username", "image"]

    date_hierarchy = "uploaded_at"


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "file",
        "user",
        "uploaded_at",
    )

    list_filter = ("user",)

    search_fields = ["user__username", "file"]

    date_hierarchy = "uploaded_at"


@admin.register(ArticleFavorite)
class ArticleFavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "favored_at")

    search_fields = ["user__username", "article__title"]

    list_filter = ["user", "article"]

    date_hierarchy = "favored_at"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "username",
        "public_name",
        "bio",
        "has_avatar",
        "subscribers_count",
        "articles_count",
        "date_joined",
    )

    search_fields = ["username", "public_name", "user__username", "bio"]

    date_hierarchy = "user__date_joined"

    def has_avatar(self, obj):
        return obj.avatar is not None

    def date_joined(self, obj):
        return obj.user.date_joined


@admin.register(ProfileSubscription)
class ProfileSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "subscribed_to", "subscribed_at")

    search_fields = ["user__username", "profile__username"]

    date_hierarchy = "subscribed_at"

    list_filter = ("user", "profile")

    def subscribed_to(self, obj):
        return obj.profile.username
