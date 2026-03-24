from django.db import models


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
