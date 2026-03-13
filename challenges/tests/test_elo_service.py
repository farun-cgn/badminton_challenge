from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import PlayerProfile
from challenges.models import Challenge, ChallengeStatus, EloHistory
from challenges import elo_service


def make_player(username, elo, rank):
    user = User.objects.create_user(username=username, password='test1234', email=f'{username}@test.com')
    profile = user.profile
    profile.elo_rating = elo
    profile.rank_position = rank
    profile.save()
    return user


class EloCalculationTest(TestCase):
    def test_equal_ratings(self):
        change = elo_service.calculate_elo_change(1200, 1200)
        self.assertEqual(change, 16)

    def test_underdog_beats_favorite(self):
        change = elo_service.calculate_elo_change(1000, 1400)
        self.assertGreater(change, 16)

    def test_favorite_beats_underdog(self):
        change = elo_service.calculate_elo_change(1400, 1000)
        self.assertLess(change, 16)

    def test_minimum_change_is_one(self):
        change = elo_service.calculate_elo_change(3000, 100)
        self.assertGreaterEqual(change, 1)

    def test_expected_score_symmetric(self):
        ea = elo_service.expected_score(1200, 1200)
        self.assertAlmostEqual(ea, 0.5, places=5)

    def test_elo_floor(self):
        low = make_player('low_elo', 105, 2)
        high = make_player('high_elo', 2000, 1)
        challenge = Challenge.objects.create(
            challenger=low,
            challenged=high,
            status=ChallengeStatus.ACCEPTED,
            challenger_elo_before=105,
            challenged_elo_before=2000,
        )
        elo_service.process_match_result(challenge, winner=high)
        low.profile.refresh_from_db()
        self.assertGreaterEqual(low.profile.elo_rating, elo_service.ELO_FLOOR)


class ChallengeWorkflowTest(TestCase):
    def setUp(self):
        self.player1 = make_player('player1', 1400, 1)
        self.player2 = make_player('player2', 1200, 2)

    def _make_challenge(self):
        return Challenge.objects.create(
            challenger=self.player2,
            challenged=self.player1,
            status=ChallengeStatus.PENDING,
            challenger_elo_before=1200,
            challenged_elo_before=1400,
        )

    def test_accept_challenge(self):
        c = self._make_challenge()
        elo_service.process_accept(c)
        c.refresh_from_db()
        self.assertEqual(c.status, ChallengeStatus.ACCEPTED)
        self.assertIsNotNone(c.responded_at)

    def test_decline_penalty_applies_elo(self):
        c = self._make_challenge()
        old_elo = self.player1.profile.elo_rating
        elo_service.process_decline_penalty(c)
        self.player1.profile.refresh_from_db()
        self.assertLess(self.player1.profile.elo_rating, old_elo)
        c.refresh_from_db()
        self.assertEqual(c.status, ChallengeStatus.DECLINED)

    def test_finalize_match_updates_elo(self):
        c = self._make_challenge()
        elo_service.process_accept(c)
        old_p1 = self.player1.profile.elo_rating
        old_p2 = self.player2.profile.elo_rating
        elo_service.finalize_match(c, winner=self.player2, score='21-15', entered_by=self.player2)
        self.player1.profile.refresh_from_db()
        self.player2.profile.refresh_from_db()
        self.assertGreater(self.player2.profile.elo_rating, old_p2)
        self.assertLess(self.player1.profile.elo_rating, old_p1)
        c.refresh_from_db()
        self.assertEqual(c.status, ChallengeStatus.COMPLETED)

    def test_rank_recomputed_after_match(self):
        # Set equal ELO so one win is enough to flip rank
        self.player1.profile.elo_rating = 1200
        self.player1.profile.save()
        self.player2.profile.elo_rating = 1200
        self.player2.profile.save()
        c = Challenge.objects.create(
            challenger=self.player2,
            challenged=self.player1,
            status=ChallengeStatus.ACCEPTED,
            challenger_elo_before=1200,
            challenged_elo_before=1200,
        )
        elo_service.finalize_match(c, winner=self.player2, score='21-15, 21-10', entered_by=self.player2)
        self.player1.profile.refresh_from_db()
        self.player2.profile.refresh_from_db()
        self.assertEqual(self.player2.profile.rank_position, 1)
        self.assertEqual(self.player1.profile.rank_position, 2)

    def test_elo_history_written(self):
        c = self._make_challenge()
        elo_service.process_accept(c)
        elo_service.finalize_match(c, winner=self.player2, score='21-18', entered_by=self.player2)
        self.assertTrue(EloHistory.objects.filter(player=self.player2, reason='match_win').exists())
        self.assertTrue(EloHistory.objects.filter(player=self.player1, reason='match_loss').exists())
