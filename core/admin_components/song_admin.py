from django.contrib import admin

from ..models import Song
from .share_link_inline import ShareLinkInline


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('song_title', 'library', 'status', 'duration_display', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'library__user__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ShareLinkInline]
    fields = (
        'library',
        'title',
        'occasion',
        'genre',
        'voice_type',
        'custom_text',
        'status',
        'duration',
        'description',
        'created_at',
        'updated_at',
    )

    def song_title(self, obj):
        return obj.title

    song_title.short_description = 'Title'

    def duration_display(self, obj):
        mins, secs = divmod(obj.duration, 60)
        return f'{mins}m {secs:02d}s'

    duration_display.short_description = 'Duration'
