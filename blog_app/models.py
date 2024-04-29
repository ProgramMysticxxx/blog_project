from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

from typing import Literal


class UploadedImage(models.Model):
    image = models.ImageField(upload_to=settings.UPLOADS_DIR + "/images/")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="uploaded_images",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} uploaded {self.image}"


class UploadedFile(models.Model):
    file = models.FileField(upload_to=settings.UPLOADS_DIR + "/files/")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="uploaded_files",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} uploaded {self.file}"


class Category(models.Model):
    name = models.CharField(
        max_length=32,
        primary_key=True,
    )

    @property
    def articles_count(self) -> int:
        return self.articles.count()

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=32,
        primary_key=True,
    )

    @property
    def articles_count(self) -> int:
        return self.articles.count()

    def __str__(self):
        return f"#{self.name}"


class Article(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="articles",
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    cover = models.ForeignKey(
        UploadedImage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="articles",
    )
    tags = models.ManyToManyField(Tag, related_name="articles")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def ratings_count(
        self,
    ) -> dict[
        Literal["positive"] | Literal["negative"],
        int,
    ]:
        return self.article_rates.aggregate(
            positive=models.Count("pk", filter=models.Q(is_positive=True)),
            negative=models.Count("pk", filter=models.Q(is_positive=False)),
        )

    # @property
    # def rating(self) -> int:
    #     return (
    #         self.article_rates.aggregate(
    #             rating=models.Sum(
    #                 models.Case(
    #                     models.When(is_positive=True, then=1),
    #                     models.When(is_positive=False, then=-1),
    #                     output_field=models.IntegerField(),
    #                 )
    #             )
    #         )["rating"]
    #         or 0
    #     )
    
    @property
    def tags_names(self):
        return self.tags.values_list("name", flat=True)

    def __str__(self):
        return f'"{self.title}" by {self.author}'


class ArticleRate(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="article_rates",
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="article_rates",
    )
    is_positive = models.BooleanField()
    rated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "article")

    def __str__(self):
        return (
            f"{self.user} {'liked' if self.is_positive else 'disliked'} {self.article}"
        )


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="comments",
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    reply_to = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        related_name="replies",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def has_replies(self):
        return self.replies.count() > 0

    @property
    def ratings_count(self) -> dict[
        Literal["positive"] | Literal["negative"],
        int,
    ]:
        return self.comment_rates.aggregate(
            positive=models.Count("pk", filter=models.Q(is_positive=True)),
            negative=models.Count("pk", filter=models.Q(is_positive=False)),
        )

    # @property
    # def rating(self) -> int:
    #     return (
    #         self.comment_rates.aggregate(
    #             rating=models.Sum(
    #                 models.Case(
    #                     models.When(is_positive=True, then=1),
    #                     models.When(is_positive=False, then=-1),
    #                     output_field=models.IntegerField(),
    #                 )
    #             )
    #         )["rating"]
    #         or 0
    #     )

    def __str__(self):
        return f'"{self.content}" by {self.user}'


class CommentRate(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comment_rates",
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="comment_rates",
    )
    is_positive = models.BooleanField()
    rated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "comment")

    # def __str__(self):
    #     return (
    #         f'{self.user} {'liked' if self.is_positive else 'disliked'} "{self.comment}"'
    #     )

class ArticleFavorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favored_articles",
    )
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="favors"
    )
    favored_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-favored_at",)
        unique_together = ("user", "article")

    def __str__(self):
        return f"{self.user} favored {self.article}"


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    username = models.CharField(max_length=150, unique=True)
    public_name = models.CharField(
        max_length=150,
        blank=True,
    )
    avatar = models.ForeignKey(
        UploadedImage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    bio = models.TextField(blank=True)

    @property
    def articles_count(self) -> int:
        return self.user.articles.count()

    @property
    def subscribers_count(self) -> int:
        return self.subscribers.count()

    @property
    def total_articles_rating(self) -> int:
        return (
            self.user.articles.aggregate(
                rating=models.Sum(
                    models.Case(
                        models.When(article_rates__is_positive=True, then=1),
                        models.When(article_rates__is_positive=False, then=-1),
                    )
                )
            )["rating"]
            or 0
        )

    def __str__(self):
        return f"{self.user.username} Profile"


class ProfileSubscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribers",
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="subscribers",
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "profile")

    def __str__(self):
        return f"{self.user} subscribed to {self.profile}"
