from django.db import models
from .enums import Occasion, Genre, VoiceType
from .song import Song


class SongParameters(models.Model):
    """
    User preferences that define and create the song.

    - title, occasion, genre, voice_type are REQUIRED.
    - custom_text is the only OPTIONAL field.
    - SongParameters is what the user fills in to generate a song.
      Creating SongParameters effectively creates the Song.
    - Always preserved even when the song fails or is retried.
    - Deleted only when the song itself is explicitly deleted.
    """
    song        = models.OneToOneField(
        Song,
        on_delete=models.CASCADE,
        related_name='parameters'
    )
    # Required fields
    title       = models.CharField(max_length=255)
    occasion    = models.CharField(max_length=20, choices=Occasion.choices)
    genre       = models.CharField(max_length=20, choices=Genre.choices)
    voice_type  = models.CharField(max_length=20, choices=VoiceType.choices)
    # Optional field
    custom_text = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'song_parameters'

    def __str__(self):
        return f"Params({self.title}, {self.occasion}, {self.genre})"
