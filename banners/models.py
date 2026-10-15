from django.db import models

class Banner(models.Model):
    title = models.CharField(max_length=200, help_text="Headline for the banner")
    subtitle = models.TextField(blank=True, help_text="Subtitle or promotional description")
    image = models.ImageField(upload_to='banners/', blank=True, null=True, help_text="Optional high-resolution banner image")
    button_text = models.CharField(max_length=60, default='Learn more', blank=True, help_text="CTA button label")
    button_link = models.CharField(max_length=255, default='#', blank=True, help_text="Destination URL for CTA button")
    order = models.IntegerField(default=0, help_text="Sort order; lower values appear first")
    is_active = models.BooleanField(default=True, help_text="Active banners appear on the homepage")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title
