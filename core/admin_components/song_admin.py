from django.contrib import admin
from django.core.exceptions import ValidationError

from ..models import Song, SongParameters
from .share_link_inline import ShareLinkInline
from .song_parameters_inline import SongParametersInline


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('song_title', 'library', 'status', 'duration_display', 'created_at')
    list_filter = ('status',)
    search_fields = ('parameters__title', 'library__user__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [SongParametersInline, ShareLinkInline]
    fields = ('library', 'status', 'duration', 'description', 'created_at', 'updated_at')

    def song_title(self, obj):
        return obj.title

    song_title.short_description = 'Title'

    def duration_display(self, obj):
        mins, secs = divmod(obj.duration, 60)
        return f'{mins}m {secs:02d}s'

    duration_display.short_description = 'Duration'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        try:
            obj.parameters
        except SongParameters.DoesNotExist:
            obj.delete()
            raise ValidationError(
                'A Song cannot be saved without Song Parameters. '
                'Please fill in Title, Occasion, Genre, and Voice Type.'
            )
