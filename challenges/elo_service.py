from django.db import transaction
from django.utils import timezone

K_FACTOR = 32
DECLINE_K_FACTOR = 16
ELO_FLOOR = 100


def expected_score(rating_a: int, rating_b: int) -> float:
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def calculate_elo_change(winner_rating: int, loser_rating: int, k: int = K_FACTOR) -> int:
    exp = expected_score(winner_rating, loser_rating)
    return max(round(k * (1 - exp)), 1)


def recompute_rank_positions() -> None:
    from accounts.models import PlayerProfile
    # Clear all positions first
    PlayerProfile.objects.filter(is_active_member=True).update(rank_position=None)
    # Rank men and women separately so each gender has its own rank 1, 2, 3, ...
    for gender in ('M', 'F'):
        profiles = list(
            PlayerProfile.objects.filter(is_active_member=True, gender=gender)
            .order_by('-elo_rating')
            .select_for_update()
        )
        for position, profile in enumerate(profiles, start=1):
            profile.rank_position = position
        PlayerProfile.objects.bulk_update(profiles, ['rank_position'])


@transaction.atomic
def process_match_result(challenge, winner, k: int = K_FACTOR,
                          reason_winner: str = 'match_win', reason_loser: str = 'match_loss') -> int:
    from .models import EloHistory, MatchResult

    loser = challenge.challenged if winner == challenge.challenger else challenge.challenger

    winner_profile = winner.profile
    loser_profile = loser.profile

    change = calculate_elo_change(winner_profile.elo_rating, loser_profile.elo_rating, k=k)

    winner_elo_before = winner_profile.elo_rating
    loser_elo_before = loser_profile.elo_rating

    winner_profile.elo_rating += change
    loser_profile.elo_rating = max(loser_profile.elo_rating - change, ELO_FLOOR)

    winner_profile.save(update_fields=['elo_rating'])
    loser_profile.save(update_fields=['elo_rating'])

    EloHistory.objects.create(
        player=winner, challenge=challenge,
        elo_before=winner_elo_before, elo_after=winner_profile.elo_rating,
        change=change, reason=reason_winner,
    )
    EloHistory.objects.create(
        player=loser, challenge=challenge,
        elo_before=loser_elo_before, elo_after=loser_profile.elo_rating,
        change=loser_profile.elo_rating - loser_elo_before,
        reason=reason_loser,
    )

    if winner == challenge.challenger:
        challenge.challenger_elo_after = winner_profile.elo_rating
        challenge.challenged_elo_after = loser_profile.elo_rating
    else:
        challenge.challenger_elo_after = loser_profile.elo_rating
        challenge.challenged_elo_after = winner_profile.elo_rating

    recompute_rank_positions()
    return change


@transaction.atomic
def process_decline_penalty(challenge) -> int:
    from django.utils import timezone
    change = process_match_result(
        challenge,
        winner=challenge.challenger,
        k=DECLINE_K_FACTOR,
        reason_winner='decline_win',
        reason_loser='decline_penalty',
    )
    challenge.status = 'declined'
    challenge.responded_at = timezone.now()
    challenge.save(update_fields=['status', 'responded_at', 'challenger_elo_after', 'challenged_elo_after'])
    return change


@transaction.atomic
def process_accept(challenge) -> None:
    from django.utils import timezone
    challenge.status = 'accepted'
    challenge.responded_at = timezone.now()
    challenge.save(update_fields=['status', 'responded_at'])


@transaction.atomic
def finalize_match(challenge, winner, score: str, entered_by) -> int:
    from .models import MatchResult
    from django.utils import timezone

    loser = challenge.challenged if winner == challenge.challenger else challenge.challenger
    change = process_match_result(challenge, winner=winner)

    MatchResult.objects.create(
        challenge=challenge,
        winner=winner,
        loser=loser,
        score=score,
        entered_by=entered_by,
        elo_change=change,
    )

    challenge.status = 'completed'
    challenge.completed_at = timezone.now()
    challenge.save(update_fields=['status', 'completed_at', 'challenger_elo_after', 'challenged_elo_after'])
    return change
