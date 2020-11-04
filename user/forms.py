from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions

from user.models import UserProfile


def check_avatar(avatar):
    if avatar:
        if avatar.size > 1 * 1024 * 1024:
            raise ValidationError("Avatar picture too big ( > 1mb )")

        width, height = get_image_dimensions(avatar.file)

        if width < 100 or height < 100:
            raise ValidationError("Avatar picture must be at least 100x100 pixels")


class SignUpForm(UserCreationForm):
    avatar = forms.ImageField(help_text='Load picture up to 1MB', required=False)

    class Meta:
        model = UserProfile
        fields = ('username', 'password1', 'password2', 'email', 'avatar')

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar', None)
        if avatar:
            check_avatar(avatar)
        return avatar

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
        return user


class UserSettings(forms.ModelForm):
    email = forms.CharField(max_length=254, required=True)
    avatar = forms.ImageField(help_text='Load picture up to 1MB', required=False)

    class Meta:
        model = UserProfile
        fields = ('email', 'avatar')

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar', None)
        check_avatar(avatar)
        return avatar
