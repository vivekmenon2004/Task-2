from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'slug', 'is_active', 'created_at')
    list_display_links = ('image_preview', 'name')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_display', 'created_at', 'updated_at')
    fields = ('name', 'slug', 'description', 'image', 'image_display', 'is_active', 'created_at', 'updated_at')
    actions = ['clear_images']

    @admin.action(description="Remove/Delete image from selected categories")
    def clear_images(self, request, queryset):
        count = 0
        for cat in queryset:
            if cat.image:
                cat.image.delete(save=False)
                cat.image = None
                cat.save()
                count += 1
        self.message_user(request, f"Image successfully removed from {count} category(ies).")

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 48px; height: 48px; object-fit: cover; border-radius: 6px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999; font-size: 11px;">No image</span>')
    image_preview.short_description = 'Thumbnail'

    def image_display(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 220px; max-width: 320px; object-fit: contain; border-radius: 8px; border: 1px solid #ccc; padding: 4px;" />',
                obj.image.url
            )
        return 'No image uploaded yet'
    image_display.short_description = 'Image Preview'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'category', 'price', 'is_featured', 'is_active', 'created_at')
    list_display_links = ('image_preview', 'name')
    list_filter = ('category', 'is_featured', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'key_specs')
    list_editable = ('is_featured', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_display', 'created_at', 'updated_at')
    fields = (
        'name',
        'slug',
        'category',
        'price',
        'key_specs',
        'description',
        'image',
        'image_display',
        'is_featured',
        'is_active',
        'created_at',
        'updated_at',
    )
    actions = ['clear_images']

    @admin.action(description="Remove/Delete image from selected products")
    def clear_images(self, request, queryset):
        count = 0
        for prod in queryset:
            if prod.image:
                prod.image.delete(save=False)
                prod.image = None
                prod.save()
                count += 1
        self.message_user(request, f"Image successfully removed from {count} product(s).")

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 48px; height: 48px; object-fit: cover; border-radius: 6px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999; font-size: 11px;">No image</span>')
    image_preview.short_description = 'Thumbnail'

    def image_display(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 260px; max-width: 360px; object-fit: contain; border-radius: 8px; border: 1px solid #ccc; padding: 4px;" />',
                obj.image.url
            )
        return 'No image uploaded yet'
    image_display.short_description = 'Image Preview'
