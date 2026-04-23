from django.contrib import admin

from ..models import ShareLink


class ShareLinkInline(admin.TabularInline):
    model = ShareLink
    extra = 0
    readonly_fields = ('token', 'is_valid_display', 'created_at')

    def is_valid_display(self, obj):
        return obj.is_valid

    is_valid_display.boolean = True
    is_valid_display.short_description = 'Valid?'
