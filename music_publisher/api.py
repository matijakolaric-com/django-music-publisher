from .models import Writer, Work, Recording, Artist, Release, Label
from rest_framework import viewsets, permissions, serializers, filters
from rest_framework.response import Response


class ArtistSimpleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Artist
        fields = ['name', 'image', 'description', 'url']

    name = serializers.CharField(source='__str__', read_only=True)


class WriterSimpleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Writer
        fields = ['name', 'image', 'description', 'url']

    name = serializers.CharField(source='__str__', read_only=True)


class LabelSimpleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Label
        fields = ['name', 'image', 'description']


class WorkSimpleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Work
        fields = ['title', 'url']


class RecordingSimpleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recording
        fields = [
            'title', 'isrc', 'duration', 'release_date', 'audio_file', 'url'
        ]


class ReleaseSimpleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Release
        fields = [
            'title', 'image', 'description', 'release_label', 'release_date', 
            'ean', 'url']
    title = serializers.CharField(source='release_title', read_only=True)
    release_label = LabelSimpleSerializer(read_only=True)


class RecordingListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recording
        fields = [
            'title', 'isrc', 'duration', 'release_date', 'audio_file',
            'artist', 'record_label', 'work', 'url'
        ]

    artist = ArtistSimpleSerializer(read_only=True)
    work = WorkSimpleSerializer(read_only=True)
    record_label = LabelSimpleSerializer(read_only=True)


class RecordingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recording
        fields = [
            'title', 'isrc', 'duration', 'release_date', 'audio_file',
            'artist', 'record_label', 'work', 'releases'
        ]

    artist = ArtistSimpleSerializer(read_only=True)
    work = WorkSimpleSerializer(read_only=True)
    releases = ReleaseSimpleSerializer(read_only=True, many=True)
    record_label = LabelSimpleSerializer(read_only=True)


class ArtistSerializer(ArtistSimpleSerializer):
    class Meta:
        model = Artist
        fields = ['name', 'image', 'description', 'recordings']

    recordings = RecordingSimpleSerializer(many=True, read_only=True)


# class RecordingSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Recording
#         fields = [
#             'title', 'isrc', 'duration', 'release_date', 'audio_file', 'artist'
#         ]
# 
#     artist = ArtistSimpleSerializer(read_only=True)


class WriterSerializer(WriterSimpleSerializer):
    class Meta:
        model = Writer
        fields = ['name', 'image', 'description', 'url', 'works']
    works = WorkSimpleSerializer(many=True, read_only=True)


class RecordingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Recording.objects.all()  # exclude(audio_file='')
    serializer_class = RecordingListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['^work__title', '^recording_title', '^version_title']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer_class = RecordingSerializer
        kwargs.pop('pk')
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializer_class(instance, *args, **kwargs)
        return Response(serializer.data)


class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Artist.objects.exclude(image='', description='').distinct()
    serializer_class = ArtistSimpleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['^last_name', '^first_name']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer_class = ArtistSerializer
        kwargs.pop('pk')
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializer_class(instance, *args, **kwargs)
        return Response(serializer.data)


class ReleaseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Release.objects.exclude(
        library__isnull=True, cd_identifier__isnull=False)  # excludes playlists
    serializer_class = ReleaseSimpleSerializer
    permission_classes = [permissions.IsAuthenticated]


class LabelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Label.objects.all()
    serializer_class = LabelSimpleSerializer
    permission_classes = [permissions.IsAuthenticated]


class WriterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Writer.objects.exclude(image='', description='').distinct()
    serializer_class = WriterSimpleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['^last_name', '^first_name']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer_class = WriterSerializer
        kwargs.pop('pk')
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializer_class(instance, *args, **kwargs)
        return Response(serializer.data)


class WorkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Work.objects.all()
    serializer_class = WorkSimpleSerializer
    permission_classes = [permissions.IsAuthenticated]