from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )


    def test_home_page(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    
    def test_pages_availability_for_auth_user(self):
        self.client.force_login(self.author)
        for name in ('notes:list', 'notes:success', 'notes:add'):
            with self.subTest(user=self.author, name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)


    def test_pages_availability_for_different_users(self):
        for user, status in ((self.author, HTTPStatus.OK),
                             (self.reader, HTTPStatus.NOT_FOUND)):
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)


    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name, args in (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,))
        ):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)


    def test_pages_availability_for_everyone(self):
        for name in ('users:signup', 'users:login', 'users:logout'):
            for user in (self.reader, None):
                with self.subTest(user=user, name=name):
                    if user:
                        self.client.force_login(user)
                    url = reverse(name)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
