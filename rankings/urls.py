from django.urls import path
from . import views

app_name = 'rankings'

urlpatterns = [
    path('', views.leaderboard, name='leaderboard'),
    path('history/', views.elo_history, name='elo_history'),
]
