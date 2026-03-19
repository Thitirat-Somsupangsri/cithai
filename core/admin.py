from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Profile, Library, Song, SongParameters, ShareLink


# ── User ──────────────────────────────────────────────────────────────────────

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('username', 'email', 'is_staff', 'date_joined')
    search_fields = ('username', 'email')


# ── Profile ──────────────────────────────────────────────────────────────────

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'gender', 'birthday')
    search_fields = ('user__username',)


# ── Library ──────────────────────────────────────────────────────────────────

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display  = ('user', 'song_count', 'is_full_display')
    search_fields = ('user__username',)

    def song_count(self, obj):
        return f"{obj.current_song_count} / {Library.MAX_SONGS}"
    song_count.short_description = 'Songs'

    def is_full_display(self, obj):
        return obj.is_full
    is_full_display.boolean = True
    is_full_display.short_description = 'Full?'


# ── SongParameters inline ────────────────────────────────────────────────────

class SongParametersInline(admin.StackedInline):
    model        = SongParameters
    extra        = 0
    can_delete   = False        # parameters must not be deleted independently
    verbose_name = 'Song Parameters'


# ── ShareLink inline ─────────────────────────────────────────────────────────

class ShareLinkInline(admin.TabularInline):
    model           = ShareLink
    extra           = 0
    readonly_fields = ('token', 'is_valid_display', 'created_at')

    def is_valid_display(self, obj):
        return obj.is_valid
    is_valid_display.boolean = True
    is_valid_display.short_description = 'Valid?'


# ── Song ─────────────────────────────────────────────────────────────────────

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display    = ('title', 'library', 'status', 'duration_display', 'created_at')
    list_filter     = ('status',)
    search_fields   = ('title', 'library__user__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines         = [SongParametersInline, ShareLinkInline]

    def duration_display(self, obj):
        mins, secs = divmod(obj.duration, 60)
        return f"{mins}m {secs:02d}s"
    duration_display.short_description = 'Duration'


# ── ShareLink ─────────────────────────────────────────────────────────────────

@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display    = ('token', 'song', 'expiration_date', 'is_active', 'is_valid_display')
    list_filter     = ('is_active',)
    readonly_fields = ('token', 'created_at')

    def is_valid_display(self, obj):
        return obj.is_valid
    is_valid_display.boolean = True
    is_valid_display.short_description = 'Valid?'