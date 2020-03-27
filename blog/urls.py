from django.urls import path
from . import views

urlpatterns = [
    path("", views.blog_index, name="posts"),
    path("<int:post_id>", views.post, name="post"),
]