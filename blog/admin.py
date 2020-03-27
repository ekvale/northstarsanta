from django.contrib import admin
from .models import Post
from tinymce import TinyMCE
from django.db import models

from django.contrib import admin
from .models import Post, Comment


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status="published")


class PostAdmin(admin.ModelAdmin):
    formfield_overrides = {models.TextField: {"widget": TinyMCE()}}
    list_display = ("title", "slug", "author", "publish", "status")
    list_filter = ("status", "created", "publish", "author")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("author",)
    date_hierarchy = "publish"
    ordering = ["status", "publish"]


admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    formfield_overrides = {models.TextField: {"widget": TinyMCE()}}
    list_display = ("name", "email", "post", "created")
    list_filter = ("created",)
    search_fields = ("name", "email", "body")


admin.site.register(Comment, CommentAdmin)