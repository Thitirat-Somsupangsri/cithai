from django.db import models


class Occasion(models.TextChoices):
    BIRTHDAY = 'birthday', 'Birthday'
    WEDDING = 'wedding', 'Wedding'
    ANNIVERSARY = 'anniversary', 'Anniversary'
    ROMANTIC_EVENT = 'romantic_event', 'Romantic Event'
    GRADUATION = 'graduation', 'Graduation'
    OTHER = 'other', 'Other'
