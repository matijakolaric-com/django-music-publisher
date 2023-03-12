from .models import (
    Writer,
    Work,
    Recording,
    Artist,
    Release,
    CommercialRelease,
    LibraryRelease,
    Label,
    Track,
    Playlist,
)
from rest_framework import viewsets, serializers, permissions, renderers
from rest_framework.response import Response
from django.utils.timezone import now
from django.http import Http404


class DjangoModelPermissionsIncludingView(permissions.DjangoModelPermissions):
    """Requires the user to have proper permissions, including view."""

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }


class ArtistNestedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Artist
        fields = ["name", "image", "description", "url"]

    name = serializers.CharField(source="__str__", read_only=True)


class LabelNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ["name", "image", "description"]


class WriterNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Writer
        fields = [
            "last_name",
            "first_name",
            "ipi_name",
            "image",
            "description",
        ]


class WriterNamesField(serializers.RelatedField):
    def to_representation(self, value):
        for writer in value.distinct():
            yield WriterNestedSerializer(writer).data


class WorkNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = ["title", "work_id", "iswc", "writers"]

    writers = WriterNamesField(read_only=True)


class ReleaseListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Release
        fields = [
            "title",
            "image",
            "description",
            "release_label",
            "release_date",
            "ean",
            "url",
        ]

    title = serializers.CharField(source="release_title", read_only=True)
    release_label = LabelNestedSerializer(read_only=True)


class ArtistField(serializers.RelatedField):
    def to_representation(self, artist):
        if artist.description or artist.image:
            yield ArtistNestedSerializer(artist, context=self.context).data
        else:
            yield ArtistPlaylistSerializer(artist).data


class RecordingInTrackSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recording
        fields = [
            "title",
            "recording_id",
            "isrc",
            "duration",
            "release_date",
            "audio_file",
            "artist",
            "record_label",
            "work",
        ]

    artist = ArtistField(read_only=True)
    work = WorkNestedSerializer(read_only=True)
    record_label = LabelNestedSerializer(read_only=True)


class TrackNestedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Track
        fields = ["cut_number", "recording"]

    recording = RecordingInTrackSerializer(read_only=True)


class ReleaseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = [
            "title",
            "artist",
            "image",
            "description",
            "release_label",
            "release_date",
            "ean",
            "tracks",
        ]

    title = serializers.CharField(source="release_title", read_only=True)
    release_label = LabelNestedSerializer(read_only=True)
    tracks = TrackNestedSerializer(many=True, read_only=True)


class ReleaseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for releases with images or descriptions.

    Requires authenticated user with appropriate ``view`` permission.

    Note that all related information, including files are included in
    this view.

    """

    queryset = (
        Release.objects.exclude(
            library__isnull=True, cd_identifier__isnull=False
        )
        .exclude(image="", description="")
        .select_related("release_label")
    )

    permission_classes = [DjangoModelPermissionsIncludingView]

    def get_serializer(self, *args, **kwargs):
        if kwargs.get("many"):
            serializer_class = ReleaseListSerializer
        else:
            serializer_class = ReleaseDetailSerializer
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)


class RecordingInArtistSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recording
        fields = [
            "title",
            "isrc",
            "duration",
            "release_date",
            "audio_file",
            "record_label",
            "work",
        ]

    work = WorkNestedSerializer(read_only=True)
    record_label = LabelNestedSerializer(read_only=True)


class ArtistDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = ["name", "image", "description", "recordings"]

    name = serializers.CharField(source="__str__", read_only=True)
    recordings = RecordingInArtistSerializer(read_only=True, many=True)


class ArtistPlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = ["name", "image", "description"]

    name = serializers.CharField(source="__str__", read_only=True)


class RecordingPlaylistSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recording
        fields = [
            "title",
            "recording_id",
            "isrc",
            "duration",
            "release_date",
            "audio_file",
            "artist",
            "record_label",
            "work",
        ]

    artist = ArtistPlaylistSerializer(read_only=True)
    work = WorkNestedSerializer(read_only=True)
    record_label = LabelNestedSerializer(read_only=True)


class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for artists with images or descriptions.

    Requires authenticated user with appropriate ``view`` permission.

    Note that all related information, including files are included in
    this view.
    """

    queryset = Artist.objects.exclude(image="", description="")

    permission_classes = [DjangoModelPermissionsIncludingView]

    def get_serializer(self, *args, **kwargs):
        if kwargs.get("many"):
            serializer_class = ArtistNestedSerializer
        else:
            serializer_class = ArtistDetailSerializer
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)


class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = [
            "release_title",
            "image",
            "description",
            "artist",
            "release_label",
            "recordings",
        ]

    artist = ArtistPlaylistSerializer(read_only=True)
    release_label = LabelNestedSerializer(read_only=True)
    recordings = RecordingPlaylistSerializer(many=True, read_only=True)


class PlaylistViewSet(viewsets.ViewSet):
    """Endpoint for retrieval of playlists, using secret URL.
    You can find the URL in the playlist ``change view``.
    """

    queryset = Playlist.objects.none()
    lookup_field = "cd_identifier"
    serializer_class = PlaylistSerializer

    def retrieve(self, request, cd_identifier=None):
        playlist = Playlist.objects.filter(cd_identifier=cd_identifier)
        playlist = playlist.exclude(release_date__lt=now())
        playlist = playlist.first()
        if playlist is None:
            raise Http404
        return Response(
            PlaylistSerializer(playlist, context={"request": request}).data
        )


class IsSuperuser(permissions.BasePermission):
    """
    Allows access only to authenticated superusers.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )


class BackupViewSet(viewsets.ViewSet):
    """Creates a large json file with all works and all related metadata."""

    permission_classes = [IsSuperuser]
    renderer_classes = [renderers.JSONRenderer]

    def list(self, request, *args, **kwargs):
        d = {}
        d.update(Work.objects.get_dict(Work.objects.all()))
        d.update(CommercialRelease.objects.get_dict(Release.objects.all()))
        return Response(d)
