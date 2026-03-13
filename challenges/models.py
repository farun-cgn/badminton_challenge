from django.db import models
from django.contrib.auth.models import User


class ChallengeStatus(models.TextChoices):
    PENDING = 'pending', 'Ausstehend'
    ACCEPTED = 'accepted', 'Angenommen'
    DECLINED = 'declined', 'Abgelehnt'
    COMPLETED = 'completed', 'Abgeschlossen'
    CANCELLED = 'cancelled', 'Abgebrochen'


class Challenge(models.Model):
    challenger = models.ForeignKey(User, on_delete=models.PROTECT, related_name='challenges_sent')
    challenged = models.ForeignKey(User, on_delete=models.PROTECT, related_name='challenges_received')
    status = models.CharField(max_length=16, choices=ChallengeStatus.choices, default=ChallengeStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    challenger_elo_before = models.IntegerField(null=True, blank=True)
    challenged_elo_before = models.IntegerField(null=True, blank=True)
    challenger_elo_after = models.IntegerField(null=True, blank=True)
    challenged_elo_after = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.challenger.username} vs {self.challenged.username} [{self.status}]"

    def get_other_player(self, user):
        return self.challenged if user == self.challenger else self.challenger


class MatchResult(models.Model):
    challenge = models.OneToOneField(Challenge, on_delete=models.PROTECT, related_name='result')
    winner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='matches_won')
    loser = models.ForeignKey(User, on_delete=models.PROTECT, related_name='matches_lost')
    score = models.CharField(max_length=64, blank=True, help_text='z.B. "21-15, 21-18"')
    entered_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='results_entered')
    entered_at = models.DateTimeField(auto_now_add=True)
    elo_change = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.winner.username} beat {self.loser.username} ({self.score})"


class EloHistory(models.Model):
    player = models.ForeignKey(User, on_delete=models.PROTECT, related_name='elo_history')
    challenge = models.ForeignKey(
        Challenge, on_delete=models.PROTECT, related_name='elo_changes', null=True, blank=True
    )
    elo_before = models.IntegerField()
    elo_after = models.IntegerField()
    change = models.IntegerField()
    reason = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        sign = '+' if self.change >= 0 else ''
        return f"{self.player.username}: {sign}{self.change} ({self.reason})"
