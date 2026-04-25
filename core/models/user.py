from django.db import models


class User(models.Model):
    username   = models.CharField(max_length=150, unique=True)
    email      = models.EmailField(unique=True)
    password   = models.CharField(max_length=128, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.username
