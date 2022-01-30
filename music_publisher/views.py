from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from .models import Playlist
from django.utils.timezone import now
from django.db.models import Q


class SecretPlaylistView(TemplateView):
    template_name = 'secret_playlist.html'

    def get_context_data(self, secret, **kwargs):
        context = super().get_context_data(**kwargs)
        context['playlist'] = get_object_or_404(
            Playlist,
            Q(cd_identifier=secret),
            Q(Q(release_date__isnull=True) | Q(release_date__gte=now()))
        )
        return context