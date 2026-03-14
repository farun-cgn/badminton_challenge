from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import models as db_models
from .models import Challenge, ChallengeStatus
from .forms import MatchResultForm
from . import elo_service


def get_active_challenge_for_player(user):
    return Challenge.objects.filter(
        db_models.Q(challenger=user) | db_models.Q(challenged=user),
        status__in=[ChallengeStatus.PENDING, ChallengeStatus.ACCEPTED]
    ).first()


@login_required
def create_challenge(request, username):
    challenged_user = get_object_or_404(User, username=username)

    if challenged_user == request.user:
        messages.error(request, 'Du kannst dich nicht selbst herausfordern.')
        return redirect('rankings:leaderboard')

    challenger_profile = request.user.profile
    challenged_profile = challenged_user.profile

    if challenged_profile.rank_position is None or challenger_profile.rank_position is None:
        messages.error(request, 'Einer der Spieler hat noch keinen Ranglistenplatz.')
        return redirect('rankings:leaderboard')

    if challenger_profile.gender != challenged_profile.gender:
        messages.error(request, 'Herausforderungen sind nur innerhalb derselben Kategorie (Herren/Damen) möglich.')
        return redirect('rankings:leaderboard')

    if challenged_profile.rank_position >= challenger_profile.rank_position:
        messages.error(request, 'Du kannst nur Spieler herausfordern, die in der Rangliste höher stehen.')
        return redirect('rankings:leaderboard')

    active = get_active_challenge_for_player(request.user)
    if active:
        messages.error(request, 'Du hast bereits eine aktive Herausforderung. Schließe diese zuerst ab.')
        return redirect('challenges:my_challenges')

    active_challenged = get_active_challenge_for_player(challenged_user)
    if active_challenged:
        messages.error(request, f'{challenged_user.username} hat bereits eine aktive Herausforderung.')
        return redirect('rankings:leaderboard')

    if request.method == 'POST':
        challenge = Challenge.objects.create(
            challenger=request.user,
            challenged=challenged_user,
            status=ChallengeStatus.PENDING,
            challenger_elo_before=challenger_profile.elo_rating,
            challenged_elo_before=challenged_profile.elo_rating,
        )
        _send_challenge_notification(request, challenge)
        messages.success(request, f'Herausforderung an {challenged_user.username} gesendet!')
        return redirect('challenges:detail', pk=challenge.pk)

    return render(request, 'challenges/challenge_create.html', {
        'challenged_user': challenged_user,
        'challenged_profile': challenged_profile,
    })


def _send_challenge_notification(request, challenge):
    from django.core.mail import send_mail
    from django.conf import settings
    email = challenge.challenged.email
    if not email:
        return
    try:
        send_mail(
            subject=f'Neue Herausforderung von {challenge.challenger.username}',
            message=(
                f'Hallo {challenge.challenged.username},\n\n'
                f'{challenge.challenger.username} hat dich zu einem Badminton-Spiel herausgefordert.\n\n'
                f'Melde dich in der App an, um die Herausforderung anzunehmen oder abzulehnen.\n\n'
                f'Viele Grüße,\nDein Badminton-Verein'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )
    except Exception:
        pass


@login_required
def challenge_detail(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    if request.user not in (challenge.challenger, challenge.challenged) and not request.user.is_staff:
        messages.error(request, 'Kein Zugriff auf diese Herausforderung.')
        return redirect('rankings:leaderboard')
    return render(request, 'challenges/challenge_detail.html', {'challenge': challenge})


@login_required
def respond_challenge(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)

    if request.user != challenge.challenged:
        messages.error(request, 'Nur der Herausgeforderte kann auf diese Herausforderung reagieren.')
        return redirect('challenges:detail', pk=pk)

    if challenge.status != ChallengeStatus.PENDING:
        messages.error(request, 'Diese Herausforderung ist nicht mehr ausstehend.')
        return redirect('challenges:detail', pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            elo_service.process_accept(challenge)
            messages.success(request, 'Herausforderung angenommen! Vereinbart einen Spieltermin.')
        elif action == 'decline':
            change = elo_service.process_decline_penalty(challenge)
            messages.warning(
                request,
                f'Herausforderung abgelehnt. Du verlierst {change} ELO-Punkte.'
            )
        return redirect('challenges:detail', pk=pk)

    return render(request, 'challenges/challenge_respond.html', {'challenge': challenge})


@login_required
def enter_result(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)

    if request.user not in (challenge.challenger, challenge.challenged):
        messages.error(request, 'Kein Zugriff.')
        return redirect('rankings:leaderboard')

    if challenge.status != ChallengeStatus.ACCEPTED:
        messages.error(request, 'Das Ergebnis kann nur für angenommene Herausforderungen eingetragen werden.')
        return redirect('challenges:detail', pk=pk)

    if request.method == 'POST':
        form = MatchResultForm(challenge, request.POST)
        if form.is_valid():
            winner_pk = int(form.cleaned_data['winner'])
            winner = User.objects.get(pk=winner_pk)
            score = form.cleaned_data.get('score', '')
            elo_service.finalize_match(challenge, winner=winner, score=score, entered_by=request.user)
            messages.success(request, f'Ergebnis eingetragen! Sieger: {winner.username}')
            return redirect('challenges:detail', pk=pk)
    else:
        form = MatchResultForm(challenge)

    return render(request, 'challenges/challenge_enter_result.html', {
        'challenge': challenge,
        'form': form,
    })


@login_required
def my_challenges(request):
    active = Challenge.objects.filter(
        db_models.Q(challenger=request.user) | db_models.Q(challenged=request.user),
        status__in=[ChallengeStatus.PENDING, ChallengeStatus.ACCEPTED]
    ).select_related('challenger', 'challenged').order_by('-created_at')

    history = Challenge.objects.filter(
        db_models.Q(challenger=request.user) | db_models.Q(challenged=request.user),
        status__in=[ChallengeStatus.COMPLETED, ChallengeStatus.DECLINED, ChallengeStatus.CANCELLED]
    ).select_related('challenger', 'challenged').order_by('-created_at')[:20]

    return render(request, 'challenges/my_challenges.html', {
        'active_challenges': active,
        'history_challenges': history,
    })
