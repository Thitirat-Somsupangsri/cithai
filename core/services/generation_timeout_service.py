from datetime import timedelta

from django.utils import timezone

from ..models import Song, SongStatus

GENERATION_TIMEOUT_SECONDS = 600  # 10 minutes


class GenerationTimeoutService:
    """
    Marks generating songs as failed when they exceed GENERATION_TIMEOUT_SECONDS.
    Called lazily on read (list / detail) — no background task required.
    """

    def expire_timed_out_songs(self, queryset):
        """
        Bulk-updates any generating songs in the queryset that have exceeded
        the timeout.  Returns the same queryset (re-evaluated after update).
        """
        cutoff = timezone.now() - timedelta(seconds=GENERATION_TIMEOUT_SECONDS)
        timed_out = queryset.filter(
            status=SongStatus.GENERATING,
            created_at__lt=cutoff,
        )
        if timed_out.exists():
            timed_out.update(
                status=SongStatus.FAILED,
                error_message=(
                    'Generation timed out after 10 minutes. '
                    'The Suno callback was never received.'
                ),
            )
        return queryset

    def expire_if_timed_out(self, song):
        """
        Checks and updates a single song instance in-place.
        Returns True if the song was just expired.
        """
        if song.status != SongStatus.GENERATING:
            return False
        cutoff = timezone.now() - timedelta(seconds=GENERATION_TIMEOUT_SECONDS)
        if song.created_at < cutoff:
            song.status = SongStatus.FAILED
            song.error_message = (
                'Generation timed out after 10 minutes. '
                'The Suno callback was never received.'
            )
            song.save(update_fields=['status', 'error_message', 'updated_at'])
            return True
        return False
