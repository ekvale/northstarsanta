from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status="published")


class Post(models.Model):
    STATUS_CHOICES = (("draft", "Draft"), ("published", "Published"))
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date="publish")
    author = models.ForeignKey(
        User, related_name="blog_posts", on_delete=models.CASCADE
    )
    photo_main = models.ImageField()
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")

    objects = models.Manager()  # The default manager.
    published = PublishedManager()  # The Dahl-specific manager.

    tags = TaggableManager()

    class Meta:
        ordering = ("-publish",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "posts:post_detail",
            args=[
                self.publish.year,
                self.publish.strftime("%m"),
                self.publish.strftime("%d"),
                self.slug,
            ],
        )


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        """ On save, timestamp """
        if not self.id:
            self.created = timezone.now()
        return super(Comment, self).save(*args, **kwargs)

    class Meta:
        ordering = ("created",)

    def __str__(self):
        return "Comment by {} on {}".format(self.name, self.post)
