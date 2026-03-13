from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RegistrationForm
from .models import PlayerProfile


def register(request):
    if request.user.is_authenticated:
        return redirect('rankings:leaderboard')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('rankings:leaderboard')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'player': request.user.profile})


def public_profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'accounts/public_profile.html', {'viewed_user': user, 'player': user.profile})
