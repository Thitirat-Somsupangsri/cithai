from datetime import timedelta

from django.utils import timezone

from ..models import Song, SongStatus
from .music_generation.strategies.mock_music_generation_strategy import (
    MOCK_AUDIO_DURATION_SECONDS,
    MOCK_AUDIO_URL,
)

MOCK_GENERATION_DELAY_SECONDS = 1


class MockGenerationCompletionService:
    def complete_ready_songs(self, queryset):
        for song in queryset.filter(provider='mock', status=SongStatus.GENERATING).iterator():
            self.complete_if_ready(song)
        return queryset

    def complete_if_ready(self, song):
        if song.provider != 'mock' or song.status != SongStatus.GENERATING:
            return False

        ready_at = timezone.now() - timedelta(seconds=MOCK_GENERATION_DELAY_SECONDS)
        if song.created_at > ready_at:
            return False

        song.status = SongStatus.READY
        song.duration = MOCK_AUDIO_DURATION_SECONDS
        song.description = (
            f"Mock song for {song.title} "
            f"({song.occasion}, {song.genre}, {song.voice_type})"
        )
        song.error_message = ''
        song.audio_url = MOCK_AUDIO_URL
        song.save(update_fields=['status', 'duration', 'description', 'error_message', 'audio_url', 'updated_at'])
        return True
