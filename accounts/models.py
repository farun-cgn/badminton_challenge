from django.db import models
from django.contrib.auth.models import User


class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    elo_rating = models.IntegerField(default=1200)
    rank_position = models.PositiveIntegerField(unique=True, null=True, blank=True)
    is_active_member = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['rank_position']

    def __str__(self):
        return f"{self.user.username} (ELO: {self.elo_rating}, Rank: {self.rank_position})"

    def has_active_challenge(self):
        from challenges.models import Challenge, ChallengeStatus
        return Challenge.objects.filter(
            models.Q(challenger=self.user) | models.Q(challenged=self.user),
            status__in=[ChallengeStatus.PENDING, ChallengeStatus.ACCEPTED]
        ).exists()
