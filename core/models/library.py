from django.db import models
from .user import User


class Library(models.Model):
    """
    Collection container owned by exactly one User.
    Max 20 songs — enforced before creating a Song.
    """
    MAX_SONGS = 20

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='library'
    )

    class Meta:
        db_table = 'library'

    @property
    def is_full(self):
        return self.songs.count() >= self.MAX_SONGS

    @property
    def song_count(self):
        return self.songs.count()

    def __str__(self):
        return f"Library({self.user.username}, {self.song_count}/{self.MAX_SONGS})"
