from django.test import TestCase
from django.urls import reverse

from user.tests.fixtures import UserFactory


class SignUpViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/user/signup')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/signup.html')


class SettingsViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user.avatar = 'default_avatar.png'
        self.user.save()
        login = self.client.login(username=self.user.username, password='12345')
        self.assertTrue(login)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/user/settings/{}/'.format(self.user.id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        print(reverse('settings', args=(self.user.id,)))
        response = self.client.get(reverse('settings', args=(self.user.id,)))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('settings', args=(self.user.id,), ))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/user_settings.html')
