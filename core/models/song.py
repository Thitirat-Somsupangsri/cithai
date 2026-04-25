from django.db import models
from django.core.validators import MaxValueValidator
from .enums import Genre, Occasion, SongStatus, VoiceType
from .library import Library


class Song(models.Model):
    """
    An AI-generated musical composition stored in a Library.

    - Generation parameters are stored directly on Song.
    - duration in seconds; max 600 s (10 minutes).
    - All songs (generating, ready, failed) live in the library.
    - Only 'ready' songs can be played, downloaded, or shared.
    """
    MAX_DURATION_SECONDS = 600  # 10 minutes

    library     = models.ForeignKey(
        Library,
        on_delete=models.CASCADE,
        related_name='songs'
    )
    title       = models.CharField(max_length=255)
    occasion    = models.CharField(max_length=20, choices=Occasion.choices)
    genre       = models.CharField(max_length=20, choices=Genre.choices)
    voice_type  = models.CharField(max_length=20, choices=VoiceType.choices)
    custom_text = models.TextField(blank=True, default='')
    provider    = models.CharField(max_length=20, default='mock')
    provider_generation_id = models.CharField(max_length=255, blank=True, default='')
    status      = models.CharField(
        max_length=20,
        choices=SongStatus.choices,
        default=SongStatus.GENERATING
    )
    duration    = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(MAX_DURATION_SECONDS)]
    )
    description = models.TextField(blank=True, default='')
    error_message = models.TextField(blank=True, default='')
    audio_url   = models.URLField(max_length=2048, blank=True, default='')
    callback_url = models.URLField(max_length=2048, blank=True, default='')
    retry_count = models.PositiveSmallIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'song'

    @property
    def is_accessible(self):
        """Only ready songs can be played, downloaded, or shared."""
        return self.status == SongStatus.READY

    def __str__(self):
        return f"Song({self.title}, {self.status})"
