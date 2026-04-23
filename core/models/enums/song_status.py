from django.db import models


class SongStatus(models.TextChoices):
    GENERATING = 'generating', 'Generating'
    READY = 'ready', 'Ready'
    FAILED = 'failed', 'Failed'
