from django.db import models
from .enums import Gender
from .user import User


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
