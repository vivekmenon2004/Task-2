from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'apple-input',
            'placeholder': 'name@example.com',
            'autocomplete': 'email'
        }),
        help_text="We'll send important store updates to this address."
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'apple-input',
            'placeholder': 'Create a secure password',
            'autocomplete': 'new-password'
        }),
        help_text="Use at least 8 characters with a mix of letters and numbers."
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'apple-input',
            'placeholder': 'Re-enter your password',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'apple-input',
                'placeholder': 'Choose a username',
                'autocomplete': 'username'
            })
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email').lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                self.add_error('password2', "Passwords do not match.")
            else:
                try:
                    # Validate against configured password validators
                    validate_password(password1)
                except ValidationError as error:
                    self.add_error('password1', error)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'apple-input',
            'placeholder': 'Username or Email',
            'autocomplete': 'username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'apple-input',
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        })
    )


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'apple-input',
            'placeholder': 'First Name',
            'autocomplete': 'given-name'
        })
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'apple-input',
            'placeholder': 'Last Name',
            'autocomplete': 'family-name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'apple-input',
            'placeholder': 'name@example.com',
            'autocomplete': 'email'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email').lower().strip()
        user_id = self.instance.pk
        if User.objects.filter(email__iexact=email).exclude(pk=user_id).exists():
            raise ValidationError("This email is already associated with another account.")
        return email
