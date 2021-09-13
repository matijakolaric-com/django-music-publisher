from django.urls import path, include
from music_publisher.royalty_calculation import RoyaltyCalculationView
from rest_framework import routers
from .api import ReleaseViewSet, ArtistViewSet
from .views import SecretPlaylistView


class APIRootView(routers.APIRootView):
    """Root of the REST API

    ``artists`` and ``releases`` give access to artists and releases with \
    public data (``image`` or ``description``), related
    objects and *all* files, including images and audio files.

    Endpoint ``artists`` requires authentication and ``view_artist``
    permission. Endpoint ``releases`` requires authentication and
    ``view_releases`` permission.

    """
    pass


router = routers.DefaultRouter()
router.APIRootView = APIRootView
router.register(r'artists', ArtistViewSet)
router.register(r'releases', ReleaseViewSet)

urlpatterns = [
    path('royalty_calculation/', RoyaltyCalculationView.as_view(),
         name='royalty_calculation'),
    path('api/v1/', include(router.urls)),
    path('secret_playlist/<slug:secret>/', SecretPlaylistView.as_view(),
         name='secret_playlist'),
]
