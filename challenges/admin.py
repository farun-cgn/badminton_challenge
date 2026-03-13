from django.contrib import admin
from django.contrib import messages
from .models import Challenge, MatchResult, EloHistory, ChallengeStatus


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('challenger', 'challenged', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'created_at')
    date_hierarchy = 'created_at'
    search_fields = ('challenger__username', 'challenged__username')
    readonly_fields = ('created_at', 'responded_at', 'completed_at',
                       'challenger_elo_before', 'challenged_elo_before',
                       'challenger_elo_after', 'challenged_elo_after')
    actions = ['cancel_challenges']

    def cancel_challenges(self, request, queryset):
        active = queryset.filter(status__in=[ChallengeStatus.PENDING, ChallengeStatus.ACCEPTED])
        count = active.update(status=ChallengeStatus.CANCELLED)
        self.message_user(request, f'{count} Herausforderung(en) abgebrochen.', messages.SUCCESS)
    cancel_challenges.short_description = 'Ausgewählte Herausforderungen abbrechen'


@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'winner', 'loser', 'score', 'elo_change', 'entered_at')
    search_fields = ('winner__username', 'loser__username')
    readonly_fields = ('entered_at', 'elo_change')


@admin.register(EloHistory)
class EloHistoryAdmin(admin.ModelAdmin):
    list_display = ('player', 'elo_before', 'elo_after', 'change', 'reason', 'created_at')
    list_filter = ('reason', 'created_at')
    search_fields = ('player__username',)
    readonly_fields = ('created_at',)
