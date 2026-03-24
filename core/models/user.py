from django.db import models


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
