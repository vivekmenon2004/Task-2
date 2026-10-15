from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="Optional category overview")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, help_text="Optional category display image")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name = 'Categories'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(help_text="Detailed product description")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in INR")
    image = models.ImageField(upload_to='products/', blank=True, null=True, help_text="Optional product showcase image")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    is_featured = models.BooleanField(default=False, help_text="Highlight on the homepage")
    is_active = models.BooleanField(default=True, help_text="Visible in storefront")
    key_specs = models.CharField(max_length=255, blank=True, help_text="Short key information text (e.g. M3 chip, 18-hr battery, Liquid Retina XDR)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})
