from .models import Writer, Work, Recording, Artist, Release, Label, Track
from rest_framework import viewsets, permissions, serializers, filters, permissions


class DjangoModelPermissionsIncludingView(permissions.DjangoModelPermissions):
    """Requires the user to have proper permissions, including view."""
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class ArtistNestedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Artist
        fields = ['name', 'image', 'description', 'url']

    name = serializers.CharField(source='__str__', read_only=True)


class LabelNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['name', 'image', 'description']


class WriterNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Writer
        fields = ['name', 'ipi_name', 'image', 'description']

    name = serializers.CharField(source='__str__', read_only=True)


class WriterNamesField(serializers.RelatedField):
    def to_representation(self, value):
        for writer in value.distinct():
            yield WriterNestedSerializer(writer).data


class WorkNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = ['title', 'iswc', 'writers']

    writers = WriterNamesField(read_only=True)


class ReleaseListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Release
        fields = [
            'title', 'image', 'description', 'release_label', 'release_date',
            'ean', 'url']
    title = serializers.CharField(source='release_title', read_only=True)
    release_label = LabelNestedSerializer(read_only=True)


class RecordingInTrackSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recording
        fields = [
            'title', 'isrc', 'duration', 'release_date', 'audio_file',
            'artist',
            'record_label',
            'work',
        ]

    artist = ArtistNestedSerializer(read_only=True)
    work = WorkNestedSerializer(read_only=True)
    record_label = LabelNestedSerializer(read_only=True)


class TrackNestedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Track
        fields = ['cut_number', 'recording']

    recording = RecordingInTrackSerializer(read_only=True)


class ReleaseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = [
            'title', 'image', 'description', 'release_label', 'release_date',
            'ean', 'tracks']
    title = serializers.CharField(source='release_title', read_only=True)
    release_label = LabelNestedSerializer(read_only=True)
    tracks = TrackNestedSerializer(many=True, read_only=True)


class ReleaseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for releases with images or descriptions.

    Requires authenticated user with appropriate ``view`` permission.

    Note that all related information, including files are included in
    this view.

    """
    queryset = Release.objects \
        .exclude(library__isnull=True, cd_identifier__isnull=False) \
        .exclude(image='', description='')\
        .select_related('release_label')

    permission_classes = [DjangoModelPermissionsIncludingView]

    def get_serializer(self, *args, **kwargs):
        if kwargs.get('many'):
            serializer_class = ReleaseListSerializer
        else:
            serializer_class = ReleaseDetailSerializer
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)


class RecordingInArtistSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recording
        fields = [
            'title', 'isrc', 'duration', 'release_date', 'audio_file',
            'record_label',
            'work',
        ]

    work = WorkNestedSerializer(read_only=True)
    record_label = LabelNestedSerializer(read_only=True)


class ArtistDetailSerializer(serializers.ModelSerializer):
    class Meta:

        model = Release
        fields = ['name', 'image', 'description', 'recordings']

    name = serializers.CharField(source='__str__', read_only=True)
    recordings = RecordingInArtistSerializer(read_only=True, many=True)


class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for artists with images or descriptions.

    Requires authenticated user with appropriate ``view`` permission.

    Note that all related information, including files are included in
    this view.
    """
    queryset = Artist.objects\
        .exclude(image='', description='')

    permission_classes = [DjangoModelPermissionsIncludingView]

    def get_serializer(self, *args, **kwargs):
        if kwargs.get('many'):
            serializer_class = ArtistNestedSerializer
        else:
            serializer_class = ArtistDetailSerializer
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)
