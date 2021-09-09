from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from .models import Playlist


class SecretPlaylistView(TemplateView):
    template_name = 'secret_playlist.html'

    def get_context_data(self, secret, **kwargs):
        context = super().get_context_data(**kwargs)
        context['playlist'] = get_object_or_404(Playlist, cd_identifier=secret)
        return context