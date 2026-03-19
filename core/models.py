from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.utils import timezone
import uuid


# ─────────────────────────────────────────────
#  Enumerations
# ─────────────────────────────────────────────

class Gender(models.TextChoices):
    MALE              = 'male',              'Male'
    FEMALE            = 'female',            'Female'
    PREFER_NOT_TO_SAY = 'prefer_not_to_say', 'Prefer not to say'


class Occasion(models.TextChoices):
    BIRTHDAY       = 'birthday',       'Birthday'
    WEDDING        = 'wedding',        'Wedding'
    ANNIVERSARY    = 'anniversary',    'Anniversary'
    ROMANTIC_EVENT = 'romantic_event', 'Romantic Event'
    GRADUATION     = 'graduation',     'Graduation'
    OTHER          = 'other',          'Other'


class Genre(models.TextChoices):
    POP       = 'pop',       'Pop'
    ROCK      = 'rock',      'Rock'
    JAZZ      = 'jazz',      'Jazz'
    CLASSICAL = 'classical', 'Classical'
    OTHER     = 'other',     'Other'


class VoiceType(models.TextChoices):
    BABY        = 'baby',        'Baby'
    GROWN_WOMAN = 'grown_woman', 'Grown Woman'
    GROWN_MAN   = 'grown_man',   'Grown Man'
    GIRL        = 'girl',        'Girl'
    BOY         = 'boy',         'Boy'


class SongStatus(models.TextChoices):
    GENERATING = 'generating', 'Generating'
    READY      = 'ready',      'Ready'
    FAILED     = 'failed',     'Failed'


# ─────────────────────────────────────────────
#  User
# ─────────────────────────────────────────────

class User(AbstractUser):
    """
    Core identity entity.
    AbstractUser supplies: username, email, password, is_active, etc.
    """
    email = models.EmailField(unique=True)

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.username


# ─────────────────────────────────────────────
#  Profile  (1-to-1 with User)
# ─────────────────────────────────────────────

class Profile(models.Model):
    """
    Personal demographic information for a User.
    Cannot exist without a User — deleted when User is deleted.
    """
    user     = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    gender   = models.CharField(max_length=20, choices=Gender.choices)
    birthday = models.DateField()

    class Meta:
        db_table = 'profile'

    def __str__(self):
        return f"Profile({self.user.username})"


# ─────────────────────────────────────────────
#  Library  (1-to-1 with User)
# ─────────────────────────────────────────────

class Library(models.Model):
    """
    Collection container owned by exactly one User.
    Business rule: max 20 songs — enforced in services.py.
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
    def current_song_count(self):
        return self.songs.count()

    def __str__(self):
        return f"Library({self.user.username}, {self.current_song_count}/{self.MAX_SONGS})"


# ─────────────────────────────────────────────
#  Song  (many-to-1 with Library)
# ─────────────────────────────────────────────

class Song(models.Model):
    """
    An AI-generated musical composition stored in a Library.
    - duration stored in seconds; max 600 s (10 min).
    - Only 'ready' songs may be played, downloaded, or shared.
    - Parameters are always preserved regardless of status (even failed).
    """
    MAX_DURATION_SECONDS = 600  # 10 minutes

    library     = models.ForeignKey(
        Library,
        on_delete=models.CASCADE,
        related_name='songs'
    )
    title       = models.CharField(max_length=255)
    status      = models.CharField(
        max_length=20,
        choices=SongStatus.choices,
        default=SongStatus.GENERATING
    )
    # stored in seconds; 0–600
    duration    = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(MAX_DURATION_SECONDS)]
    )
    description = models.TextField(blank=True, default='')
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


# ─────────────────────────────────────────────
#  SongParameters  (1-to-1 with Song — Value Object)
# ─────────────────────────────────────────────

class SongParameters(models.Model):
    """
    User preferences that guided song generation.
    Always preserved — even when a song fails or is retried.
    Deleted only when the song itself is explicitly deleted by the user.
    custom_text is the only optional field.
    """
    song        = models.OneToOneField(
        Song,
        on_delete=models.CASCADE,
        related_name='parameters'
    )
    title       = models.CharField(max_length=255)
    occasion    = models.CharField(max_length=20, choices=Occasion.choices)
    genre       = models.CharField(max_length=20, choices=Genre.choices)
    voice_type  = models.CharField(max_length=20, choices=VoiceType.choices)
    custom_text = models.TextField(blank=True, default='')  # optional

    class Meta:
        db_table = 'song_parameters'

    def __str__(self):
        return f"Params(song={self.song_id}, {self.occasion}, {self.genre})"


# ─────────────────────────────────────────────
#  ShareLink  (many-to-1 with Song)
# ─────────────────────────────────────────────

class ShareLink(models.Model):
    """
    Temporary access token for sharing a Song.
    Valid only when is_active=True AND expiration_date >= today.
    Songs are private by default (no ShareLink exists).
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
        return self.is_active and self.expiration_date >= timezone.now().date()

    def __str__(self):
        return f"ShareLink(song={self.song_id}, valid={self.is_valid})"