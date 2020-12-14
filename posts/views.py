from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Group, Post, User, Follow
from .settings import PAGINATOR_PAGE_SIZE


def index(request):
    posts = Post.objects.select_related("group")
    paginator = Paginator(posts, PAGINATOR_PAGE_SIZE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, "index.html", {
        "page": page,
        "paginator": paginator
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related("group")
    paginator = Paginator(posts, PAGINATOR_PAGE_SIZE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, "group.html", {
        "group": group,
        "page": page,
        "paginator": paginator
    })


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if form.is_valid():
        new_form = form.save(commit=False)
        new_form.author = request.user
        new_form.save()
        return redirect("index")
    form = PostForm()
    return render(request, "new.html", {"form": form})


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(
        author=user_profile
    ).select_related("group")
    paginator = Paginator(posts, PAGINATOR_PAGE_SIZE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    user = request.user
    followed_count = Follow.objects.filter(author=user_profile).count()
    following_count = Follow.objects.filter(user=user_profile).count()
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=user_profile
        ).exists()
    else:
        following = None
    return render(request, "profile.html", {
        "page": page,
        "user": user,
        "user_profile": user_profile,
        "paginator": paginator,
        "followed_count": followed_count,
        "following_count": following_count,
        "following": following
    })


def post_view(request, username, post_id):
    try:
        post = get_object_or_404(Post, id=post_id, author__username=username)
    except Http404:
        return redirect(
            "post",
            username=Post.objects.get(id=post_id).author.username,
            post_id=post_id
        )
    comments = Comment.objects.filter(
        post__id=post_id
    ).select_related("author")
    user_profile = post.author
    post_count = user_profile.posts.count()
    user = request.user
    followed_count = Follow.objects.filter(author=user_profile).count()
    following_count = Follow.objects.filter(user=user_profile).count()
    form = CommentForm()
    return render(request, "post.html", {
        "post": post,
        "user": user,
        "post_id": post_id,
        "post_count": post_count,
        "user_profile": user_profile,
        "comments": comments,
        "form": form,
        "followed_count": followed_count,
        "following_count": following_count,
    })


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if post.author != request.user:
        return redirect("post", username=username, post_id=post_id)
    form = PostForm(
        data=request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect("post", username=username, post_id=post_id)
    return render(request, "new.html", {"form": form, "post": post})


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        new_form = form.save(commit=False)
        new_form.post = Post.objects.get(id=post_id)
        new_form.author = request.user
        new_form.save()
        return redirect(post_view, username=username, post_id=post_id)
    form = CommentForm()
    return render(request, "comment.html", {"form": form})


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, PAGINATOR_PAGE_SIZE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {
        "page": page,
        "paginator": paginator
    })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author).exists()
    if not follow and author != request.user:
        Follow.objects.create(user=request.user, author=author)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author)
    if follow:
        follow.delete()
    return redirect("profile", username=username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
