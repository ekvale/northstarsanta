from django.shortcuts import render, get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from datetime import datetime, timedelta, time
from django.utils import timezone
from taggit.models import Tag
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm
from .models import Post, Comment
from django.core.mail import send_mail
from django.db.models import Count
# from haystack.query import SearchQuerySet


def blog_index(request, tag_slug=None):
    posts = Post.objects.order_by("publish")
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])
    paginator = Paginator(posts, 3)
    page = request.GET.get("page")
    paged_posts = paginator.get_page(page)

    context = {"posts": paged_posts, "tag": tag}
    return render(request, "posts/posts.html", context)


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 3
    template_name = "posts/posts.html"


def post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.order_by("created").reverse()
    if request.method == "POST":
        # A comment was posted
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()

    comment_form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list("id", flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by(
        "-same_tags", "-publish"
    )[:4]

    context = {
        "post": post,
        "comments": comments,
        "comment_form": comment_form,
        "similar_posts": similar_posts,
    }
    return render(request, "posts/post.html", context)


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status="published")
    sent = False

    if request.method == "POST":
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(
                cd["name"], cd["email"], post.title
            )
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(
                post.title, post_url, cd["name"], cd["comments"]
            )
            send_mail(subject, message, "admin@myblog.com", [cd["to"]])
            sent = True
    else:
        form = EmailPostForm()

    context = {"post": post, "form": form, "sent": sent}
    return render(request, "posts/post/share.html", context)


def post_search(request):
    form = SearchForm()
    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            results = (
                SearchQuerySet().models(Post).filter(content=cd["query"]).load_all()
            )
            # count total results
            total_results = results.count()
    context = {
        "form": form,
        "cd": cd,
        "results": results,
        "total_results": total_results,
    }
    return render(request, "posts/post/search.html", context)
