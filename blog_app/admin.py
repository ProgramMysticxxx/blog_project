from django.contrib import admin

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

admin.site.register(Article)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(ArticleRate)
admin.site.register(Comment)
admin.site.register(CommentRate)
admin.site.register(UploadedImage)
admin.site.register(UploadedFile)
admin.site.register(ArticleFavorite)
admin.site.register(Profile)
admin.site.register(ProfileSubscription)
