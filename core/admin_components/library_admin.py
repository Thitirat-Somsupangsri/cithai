from django.contrib import admin

from ..models import Library


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ('user', 'song_count_display', 'is_full_display')
    search_fields = ('user__username',)

    def song_count_display(self, obj):
        return f'{obj.song_count} / {Library.MAX_SONGS}'

    song_count_display.short_description = 'Songs'

    def is_full_display(self, obj):
        return obj.is_full

    is_full_display.boolean = True
    is_full_display.short_description = 'Full?'
