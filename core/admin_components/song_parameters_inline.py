from django.contrib import admin

from ..models import SongParameters
from .song_parameters_inline_form import SongParametersInlineForm


class SongParametersInline(admin.StackedInline):
    model = SongParameters
    form = SongParametersInlineForm
    extra = 1
    min_num = 1
    can_delete = False
    verbose_name = 'Song Parameters'
    verbose_name_plural = 'Song Parameters (required — fill in all fields except custom text)'
