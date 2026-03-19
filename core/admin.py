"""
admin.py
--------
CRUD interface for Exercise 3 Task 4.

Key design:
- Song CANNOT be saved without SongParameters filled in.
  title, occasion, genre, voice_type are required.
  custom_text is optional.
- Song has no title field — title is displayed from parameters.
"""

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import User, Profile, Library, Song, SongParameters, ShareLink


# ── User ──────────────────────────────────────────────────────────────────────

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display  = ('username', 'email', 'created_at')
    search_fields = ('username', 'email')


# ── Profile ───────────────────────────────────────────────────────────────────

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'gender', 'birthday')
    search_fields = ('user__username',)


# ── Library ───────────────────────────────────────────────────────────────────

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display  = ('user', 'song_count_display', 'is_full_display')
    search_fields = ('user__username',)

    def song_count_display(self, obj):
        return f"{obj.song_count} / {Library.MAX_SONGS}"
    song_count_display.short_description = 'Songs'

    def is_full_display(self, obj):
        return obj.is_full
    is_full_display.boolean = True
    is_full_display.short_description = 'Full?'


# ── SongParameters inline form ────────────────────────────────────────────────
# Forces title, occasion, genre, voice_type to be filled in.

class SongParametersInlineForm(forms.ModelForm):
    class Meta:
        model  = SongParameters
        fields = ('title', 'occasion', 'genre', 'voice_type', 'custom_text')

    def clean(self):
        cleaned = super().clean()
        # If the inline row is not being deleted and not empty, require all fields
        if not self.cleaned_data.get('DELETE', False):
            required_fields = ['title', 'occasion', 'genre', 'voice_type']
            for field in required_fields:
                if not cleaned.get(field):
                    self.add_error(field, f'{field.replace("_", " ").title()} is required.')
        return cleaned


class SongParametersInline(admin.StackedInline):
    model      = SongParameters
    form       = SongParametersInlineForm
    extra      = 1
    min_num    = 1          # require at least 1 SongParameters
    can_delete = False
    verbose_name = 'Song Parameters'
    verbose_name_plural = 'Song Parameters (required — fill in all fields except custom text)'


# ── ShareLink inline ──────────────────────────────────────────────────────────

class ShareLinkInline(admin.TabularInline):
    model           = ShareLink
    extra           = 0
    readonly_fields = ('token', 'is_valid_display', 'created_at')

    def is_valid_display(self, obj):
        return obj.is_valid
    is_valid_display.boolean = True
    is_valid_display.short_description = 'Valid?'


# ── Song ──────────────────────────────────────────────────────────────────────

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display    = ('song_title', 'library', 'status', 'duration_display', 'created_at')
    list_filter     = ('status',)
    search_fields   = ('parameters__title', 'library__user__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines         = [SongParametersInline, ShareLinkInline]
    fields          = ('library', 'status', 'duration', 'description', 'created_at', 'updated_at')

    def song_title(self, obj):
        return obj.title
    song_title.short_description = 'Title'

    def duration_display(self, obj):
        mins, secs = divmod(obj.duration, 60)
        return f"{mins}m {secs:02d}s"
    duration_display.short_description = 'Duration'

    def save_model(self, request, obj, form, change):
        """
        Block saving a Song if SongParameters inline has not been filled in.
        This prevents (no title) songs from being created.
        """
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        """
        After saving the Song, check that SongParameters was actually saved.
        If not (user left the inline blank), raise an error.
        """
        super().save_related(request, form, formsets, change)
        obj = form.instance
        try:
            obj.parameters  # check parameters exist
        except SongParameters.DoesNotExist:
            # Delete the orphan Song and raise error
            obj.delete()
            raise ValidationError(
                "A Song cannot be saved without Song Parameters. "
                "Please fill in Title, Occasion, Genre, and Voice Type."
            )


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