from django.contrib import admin

from ..models import ShareLink


@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display = ('token', 'song', 'expiration_date', 'is_active', 'is_valid_display')
    list_filter = ('is_active',)
    readonly_fields = ('token', 'created_at')

    def is_valid_display(self, obj):
        return obj.is_valid

    is_valid_display.boolean = True
    is_valid_display.short_description = 'Valid?'
