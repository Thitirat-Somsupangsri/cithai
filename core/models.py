from django.db import models
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

class User(models.Model):
    """
    Registered individual.
    Plain model — authentication is out of scope for Exercise 3.
    """
    username   = models.CharField(max_length=150, unique=True)
    email      = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

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


# ─────────────────────────────────────────────
#  Song  (many-to-1 with Library)
# ─────────────────────────────────────────────

class Song(models.Model):
    """
    An AI-generated musical composition stored in a Library.

    - Song has NO title field of its own.
      The title comes from SongParameters.title — the user provides it
      as part of the generation parameters, and SongParameters creates the Song.
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
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'song'

    @property
    def title(self):
        """Title is owned by SongParameters, not Song."""
        try:
            return self.parameters.title
        except SongParameters.DoesNotExist:
            return '(no title)'

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


# ─────────────────────────────────────────────
#  ShareLink  (many-to-1 with Song)
# ─────────────────────────────────────────────

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