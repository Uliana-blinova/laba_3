

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Post, Profile
from .forms import ProfileForm


def home(request):
    posts = Post.objects.select_related('author').order_by('-created_at')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/home.html', {'page_obj': page_obj})


def profile_view(request, user_id):
    return render(request, 'blog/profile_view.html', {'user_id': user_id})


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
    return render(request, 'blog/profile_view.html', {'user_id': user_id})

@login_required
def profile_edit(request):
    return render(request, 'blog/profile_edit.html')

@login_required
def profile_delete(request):
    return render(request, 'blog/profile_delete.html')


@login_required
def post_create(request):
    return render(request, 'blog/post_form.html', {'title': 'Создать пост'})

def post_detail(request, post_id):
    return render(request, 'blog/post_detail.html', {'post_id': post_id})

@login_required
def post_edit(request, post_id):
    return render(request, 'blog/post_form.html', {'title': 'Редактировать пост', 'post_id': post_id})

@login_required
def post_delete(request, post_id):
    return render(request, 'blog/post_confirm_delete.html', {'post_id': post_id})


@login_required
def comment_edit(request, comment_id):
    return render(request, 'blog/comment_form.html', {'comment_id': comment_id})

@login_required
def comment_delete(request, comment_id):
    return render(request, 'blog/comment_confirm_delete.html', {'comment_id': comment_id})


@login_required
def like_post(request, post_id):
    # Пока просто перенаправляем
    from django.shortcuts import redirect
    return redirect('post_detail', post_id=post_id)

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