from django.urls import path
from . import views

app_name = 'challenges'

urlpatterns = [
    path('new/<str:username>/', views.create_challenge, name='create'),
    path('<int:pk>/', views.challenge_detail, name='detail'),
    path('<int:pk>/respond/', views.respond_challenge, name='respond'),
    path('<int:pk>/result/', views.enter_result, name='enter_result'),
    path('my/', views.my_challenges, name='my_challenges'),
]
