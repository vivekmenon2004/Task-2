from django.contrib import admin
from django.utils.html import format_html
from .models import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'title', 'order', 'is_active', 'button_text', 'created_at')
    list_display_links = ('image_preview', 'title')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'subtitle', 'button_text', 'button_link')
    list_editable = ('order', 'is_active')
    readonly_fields = ('image_display', 'created_at')
    fields = ('title', 'subtitle', 'image', 'image_display', 'button_text', 'button_link', 'order', 'is_active', 'created_at')

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 80px; height: 45px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999; font-size: 11px;">No image</span>')
    image_preview.short_description = 'Thumbnail'

    def image_display(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 480px; object-fit: contain; border-radius: 8px; border: 1px solid #ccc; padding: 4px;" />',
                obj.image.url
            )
        return 'No image uploaded yet'
    image_display.short_description = 'Image Preview'
