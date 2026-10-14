from django import forms
from django.contrib.auth import get_user_model
from store.models import Product, Category
from banners.models import Banner

User = get_user_model()


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'slug', 'category', 'price', 'image', 'key_specs', 'description', 'is_featured', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'dash-form-input', 'placeholder': 'e.g. MacBook Pro 16'}),
            'slug': forms.TextInput(attrs={'class': 'dash-form-input', 'placeholder': 'Leave blank to auto-generate from name'}),
            'category': forms.Select(attrs={'class': 'dash-form-select'}),
            'price': forms.NumberInput(attrs={'class': 'dash-form-input', 'step': '0.01', 'placeholder': 'Price in INR (e.g. 199900.00)'}),
            'image': forms.FileInput(attrs={'class': 'dash-form-file'}),
            'key_specs': forms.TextInput(attrs={'class': 'dash-form-input', 'placeholder': 'e.g. M3 Pro chip, 18-hr battery, Liquid Retina XDR'}),
            'description': forms.Textarea(attrs={'class': 'dash-form-textarea', 'rows': 5, 'placeholder': 'Detailed product description and specs...'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'dash-form-checkbox'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'dash-form-checkbox'}),
        }
        help_texts = {
            'slug': 'Unique URL identifier. If left empty, it will be automatically generated from the title.',
            'image': 'High quality product showcase photo.',
            'is_featured': 'Display prominently in the Featured section on the home page.',
            'is_active': 'Visible to customers across the storefront.',
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'dash-form-input', 'placeholder': 'e.g. Laptops, Displays, Audio'}),
            'slug': forms.TextInput(attrs={'class': 'dash-form-input', 'placeholder': 'Leave blank to auto-generate from name'}),
            'description': forms.Textarea(attrs={'class': 'dash-form-textarea', 'rows': 4, 'placeholder': 'Brief description of this collection...'}),
            'image': forms.FileInput(attrs={'class': 'dash-form-file'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'dash-form-checkbox'}),
        }
        help_texts = {
            'slug': 'Slug used in URLs like /category/laptops/. Auto-generated if left blank.',
            'is_active': 'Displays in navigation menus and category catalog.',
        }


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'subtitle', 'image', 'button_text', 'button_link', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'dash-form-input', 'placeholder': 'e.g. MacBook Pro — Mind-blowing. Head-turning.'}),
            'subtitle': forms.Textarea(attrs={'class': 'dash-form-textarea', 'rows': 3, 'placeholder': 'Catchy promo text or tagline...'}),
            'image': forms.FileInput(attrs={'class': 'dash-form-file'}),
            'button_text': forms.TextInput(attrs={'class': 'dash-form-input', 'placeholder': 'e.g. Learn more, Buy now'}),
            'button_link': forms.TextInput(attrs={'class': 'dash-form-input', 'placeholder': 'e.g. /products/ or /product/macbook-pro-16/'}),
            'order': forms.NumberInput(attrs={'class': 'dash-form-input', 'placeholder': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'dash-form-checkbox'}),
        }
        help_texts = {
            'order': 'Carousel slide position; lower numbers appear first.',
            'is_active': 'Displays actively in the homepage hero slider.',
        }


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'dash-form-input', 'placeholder': 'Minimum 8 characters'}),
        help_text="Set an initial password for the user."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'is_staff', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'dash-form-input', 'placeholder': 'e.g. alex_stone'}),
            'email': forms.EmailInput(attrs={'class': 'dash-form-input', 'placeholder': 'alex@example.com'}),
            'first_name': forms.TextInput(attrs={'class': 'dash-form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'dash-form-input', 'placeholder': 'Last Name'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'dash-form-checkbox'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'dash-form-checkbox'}),
        }
        help_texts = {
            'is_staff': 'Allows access to the Dashboard and administrative features.',
            'is_active': 'Determines if this user account can log in.',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'dash-form-input', 'placeholder': 'Leave blank to keep current password'}),
        help_text="Optional: enter a new password to reset it for this user."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'dash-form-input'}),
            'email': forms.EmailInput(attrs={'class': 'dash-form-input'}),
            'first_name': forms.TextInput(attrs={'class': 'dash-form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'dash-form-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'dash-form-checkbox'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'dash-form-checkbox'}),
        }
        help_texts = {
            'is_staff': 'Grants access to the Operations Dashboard.',
            'is_active': 'Account enabled or suspended.',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        new_pw = self.cleaned_data.get('new_password')
        if new_pw:
            user.set_password(new_pw)
        if commit:
            user.save()
        return user
