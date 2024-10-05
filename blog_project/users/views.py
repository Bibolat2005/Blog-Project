from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from .models import Follow, User, Profile
from .forms import ProfileForm
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('profile_detail', username=user.username)
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)

    form = None

    if request.method == 'POST':
        if request.user == user:
            form = ProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                return redirect('profile_detail', username=user.username)
        else:
            if 'follow' in request.POST:
                if request.user != user:  
                    Follow.objects.get_or_create(follower=request.user, following=user)
            elif 'unfollow' in request.POST:
                Follow.objects.filter(follower=request.user, following=user).delete()
    else:
        if request.user == user:
            form = ProfileForm(instance=profile)

    is_following = Follow.objects.filter(follower=request.user, following=user).exists()

    followers_count = Follow.objects.filter(following=user).count()  # Количество подписчиков
    following_count = Follow.objects.filter(follower=user).count()  # Количество подписок

    followers = Follow.objects.filter(following=user).values_list('follower__username', flat=True)  # Список подписчиков
    following_users = Follow.objects.filter(follower=user).values_list('following__username', flat=True)  # Список пользователей, на которых подписан

    return render(request, 'users/profile.html', {
        'profile': profile,
        'form': form,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        'followers': followers,
        'following_users': following_users,  # Передаем список пользователей, на которых подписан
        'MEDIA_URL': settings.MEDIA_URL,
    })


def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_detail', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'users/profile.html', {'form': form}) 
#сделал так, чтобы только авторизованный юзер ,смог редактировать только свой профиль прямой в профиле 

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    
    if request.user != user_to_follow:  
        Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
        
    return redirect('profile_detail', username=username)

@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    
    if request.user != user_to_unfollow: 
        Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
        
    return redirect('profile_detail', username=username)

def redirect_to_profile(request):
    if request.user.is_authenticated:
        return redirect(reverse('profile_detail', kwargs={'username': request.user.username}))
    return redirect('login')