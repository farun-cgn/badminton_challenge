from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from .models import PlayerProfile
from challenges.elo_service import recompute_rank_positions


class PlayerProfileInline(admin.StackedInline):
    model = PlayerProfile
    can_delete = False
    verbose_name = 'Spielerprofil'
    verbose_name_plural = 'Spielerprofil'
    fields = ('gender', 'elo_rating', 'rank_position', 'is_active_member')


class CustomUserAdmin(UserAdmin):
    inlines = [PlayerProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_elo', 'get_rank', 'is_staff')
    actions = ['send_password_reset', 'set_elo_1200']

    def get_elo(self, obj):
        try:
            return obj.profile.elo_rating
        except PlayerProfile.DoesNotExist:
            return '-'
    get_elo.short_description = 'ELO'

    def get_rank(self, obj):
        try:
            return obj.profile.rank_position
        except PlayerProfile.DoesNotExist:
            return '-'
    get_rank.short_description = 'Rang'

    def send_password_reset(self, request, queryset):
        sent = 0
        for user in queryset:
            if user.email:
                form = PasswordResetForm({'email': user.email})
                if form.is_valid():
                    form.save(request=request)
                    sent += 1
        self.message_user(request, f"Passwort-Reset-E-Mail an {sent} Spieler gesendet.", messages.SUCCESS)
    send_password_reset.short_description = 'Passwort-Reset-E-Mail senden'

    def set_elo_1200(self, request, queryset):
        from challenges.models import EloHistory
        from django.utils import timezone
        for user in queryset:
            try:
                profile = user.profile
                old_elo = profile.elo_rating
                profile.elo_rating = 1200
                profile.save(update_fields=['elo_rating'])
                EloHistory.objects.create(
                    player=user,
                    challenge=None,
                    elo_before=old_elo,
                    elo_after=1200,
                    change=1200 - old_elo,
                    reason='admin_set',
                )
            except PlayerProfile.DoesNotExist:
                pass
        recompute_rank_positions()
        self.message_user(request, f"ELO auf 1200 zurückgesetzt für {queryset.count()} Spieler.", messages.SUCCESS)
    set_elo_1200.short_description = 'ELO auf 1200 setzen'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
