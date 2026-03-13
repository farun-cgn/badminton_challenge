from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.http import HttpResponse


def health_check(request):
    return HttpResponse('OK')


def root_redirect(request):
    return redirect('rankings:leaderboard')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('challenges/', include('challenges.urls', namespace='challenges')),
    path('rankings/', include('rankings.urls', namespace='rankings')),
    path('health/', health_check, name='health'),
    path('', root_redirect, name='root'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
