from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from .models import Post, Profile, Comment,  Like
from django.db.models import Count

def home(request):
    if not request.user.is_authenticated:
        return render(request, 'blog/home.html', {
            'page_obj': None,
            'show_login_message': True
        })

    posts = Post.objects.select_related('author').annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True),
    ).order_by('-created_at')[:50]

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/home.html', {'page_obj': page_obj})

def profile_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    print(f"Найдено постов для {user.username}: {posts.count()}")  # ← дебаг
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/profile_view.html', {
        'profile_user': user,
        'page_obj': page_obj,
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            from .models import Profile
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Аккаунт {user.username} создан!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'blog/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'blog/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def profile_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/profile_view.html', {
        'profile_user': user,  # ← важно!
        'page_obj': page_obj,
    })

@login_required
def profile_edit(request):
    return render(request, 'blog/profile_edit.html')

@login_required
def profile_delete(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Ваш профиль удалён.')
        return redirect('home')
    return render(request, 'blog/profile_delete.html')


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Пост опубликован!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Новый пост'})

from .forms import ProfileForm, PostForm, CommentForm

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.select_related('author').order_by('created_at')

    if request.user.is_authenticated:
        post.liked = Like.objects.filter(post=post, user=request.user).exists()
    else:
        post.liked = False

    if request.user.is_authenticated:
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                messages.success(request, 'Комментарий добавлен!')
                return redirect('post_detail', post_id=post.id)
        else:
            form = CommentForm()
    else:
        form = None

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })
@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост обновлён!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Редактировать пост'})

@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост удалён.')
        return redirect('profile_view', user_id=request.user.id)
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


@login_required
def comment_edit(request, comment_id):
    return render(request, 'blog/comment_form.html', {'comment_id': comment_id})

@login_required
def comment_delete(request, comment_id):
    return render(request, 'blog/comment_confirm_delete.html', {'comment_id': comment_id})



@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён!')
            return redirect('profile_view', user_id=request.user.id)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'blog/profile_edit.html', {'form': form})
@login_required
def profile_delete(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Ваш профиль удалён.')
        return redirect('home')
    return render(request, 'blog/profile_delete.html')
@login_required
def comment_edit(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Комментарий обновлён!')
            return redirect('post_detail', post_id=comment.post.id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/comment_form.html', {'form': form, 'comment': comment})


@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    if request.method == 'POST':
        post_id = comment.post.id
        comment.delete()
        messages.success(request, 'Комментарий удалён.')
        return redirect('post_detail', post_id=post_id)
    return render(request, 'blog/comment_confirm_delete.html', {'comment': comment})