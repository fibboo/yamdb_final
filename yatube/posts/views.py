from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page
from rest_framework import viewsets

from .forms import PostForm, CommentForm
from .models import Post, Group, Comment, Follow
from .serializers import PostSerializer


@cache_page(20)
def index(request):
    post_list = Post.objects.prefetch_related('author').all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {'page': page}

    return render(request, 'index.html', context)


@cache_page(20)
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.prefetch_related('author').all()
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {'group': group, 'page': page}

    return render(request, 'group.html', context)


def get_groups(request):
    groups = Group.objects.all()
    context = {'groups': groups, 'nav_bar': 'groups'}

    return render(request, 'groups.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author__username=username)
    paginator = Paginator(posts, 10)
    page = paginator.get_page(request.GET.get('page'))

    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()

    context = {
        'page': page,
        'author': author,
        'following': following,
    }

    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    comments = Comment.objects.filter(post_id=post_id).all()
    form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': form
    }

    return render(request, 'post.html', context)


@login_required()
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')

    context = {'form': form, 'nav_bar': 'new_post', 'new': True}
    return render(request, 'new_post.html', context)


@login_required()
def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect('post', username, post_id)

    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)

    context = {'form': form, 'post': post}
    return render(request, 'new_post.html', context)


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required()
def add_comment(request, username, post_id):
    post = Post.objects.get(author__username=username, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('post', post.author, post_id)


@login_required
@cache_page(20)
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)

    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {'page': page}
    return render(request, "follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)

    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author__username=username
    ).delete()
    return redirect('profile', username)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
