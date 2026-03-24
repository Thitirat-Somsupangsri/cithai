import uuid
from django.db import models
from django.utils import timezone
from .song import Song


class ShareLink(models.Model):
    """
    Temporary access token for sharing a Song.
    Valid only when is_active=True AND expiration_date >= today.
    Songs are private by default — no ShareLink exists until created.
    Deleted when its Song is deleted.
    """
    song            = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='share_links'
    )
    token           = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expiration_date = models.DateField()
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'share_link'

    @property
    def is_valid(self):
        if not self.expiration_date:
            return False
        return self.is_active and self.expiration_date >= timezone.now().date()

    def __str__(self):
        return f"ShareLink(song={self.song_id}, valid={self.is_valid})"
