from django.urls import path, include
from music_publisher.royalty_calculation import RoyaltyCalculationView
from rest_framework import routers
from .api import ReleaseViewSet, ArtistViewSet
# WriterViewSet, RecordingViewSet, ArtistViewSet, ReleaseViewSet, WorkViewSet

router = routers.DefaultRouter()
router.register(r'artists', ArtistViewSet)
router.register(r'releases', ReleaseViewSet)

urlpatterns = [
    path('royalty_calculation/', RoyaltyCalculationView.as_view(),
         name='royalty_calculation'),
    path('api/v1/', include(router.urls)),
]
