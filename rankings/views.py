from django.shortcuts import render
from django.core.paginator import Paginator
from accounts.models import PlayerProfile
from challenges.models import EloHistory


def leaderboard(request):
    players = PlayerProfile.objects.filter(is_active_member=True).select_related('user').order_by('rank_position')
    return render(request, 'rankings/leaderboard.html', {'players': players})


def elo_history(request):
    history = EloHistory.objects.select_related('player', 'challenge').order_by('-created_at')
    paginator = Paginator(history, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'rankings/elo_history.html', {'page_obj': page})
