from django.test import TestCase

from user.forms import SignUpForm, UserSettings


class SignUpFormTest(TestCase):
    def test_signup_form_avatar_help_text(self):
        form = SignUpForm()
        self.assertEqual(form.fields['avatar'].help_text, 'Load picture up to 1MB')


class UserSettingsFormTest(TestCase):
    def test_signup_form_avatar_help_text(self):
        form = UserSettings()
        self.assertEqual(form.fields['avatar'].help_text, 'Load picture up to 1MB')
