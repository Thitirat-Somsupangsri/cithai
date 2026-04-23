from django.db import models


class VoiceType(models.TextChoices):
    BABY = 'baby', 'Baby'
    GROWN_WOMAN = 'grown_woman', 'Grown Woman'
    GROWN_MAN = 'grown_man', 'Grown Man'
    GIRL = 'girl', 'Girl'
    BOY = 'boy', 'Boy'
