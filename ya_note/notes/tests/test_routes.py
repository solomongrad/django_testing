from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
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
        cls.HOME_URL = reverse('notes:home')
        cls.LIST_URL = reverse('notes:list')
        cls.ADD_URL = reverse('notes:add')
        cls.SUCCESS_URL = reverse('notes:success')
        cls.LOGIN_URL = reverse('users:login')
        cls.SIGNUP_URL = reverse('users:signup')
        cls.LOGOUT_URL = reverse('users:logout')
        cls.SLUG = cls.note.slug
        cls.EDIT_URL = reverse('notes:edit', args=(cls.SLUG,))
        cls.DETAIL_URL = reverse('notes:detail', args=(cls.SLUG,))
        cls.DELETE_URL = reverse('notes:delete', args=(cls.SLUG,))

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)
        self.urls_tuple = (self.EDIT_URL,
                           self.DETAIL_URL,
                           self.DELETE_URL,
                           self.HOME_URL,
                           self.LIST_URL,
                           self.ADD_URL,
                           self.SUCCESS_URL,
                           self.LOGIN_URL,
                           self.SIGNUP_URL,
                           self.LOGOUT_URL,)

    def test_pages_availability_for_author(self):
        for name in self.urls_tuple:
            with self.subTest(name=name):
                response = self.author_client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_other_user(self):
        not_avaible = (self.EDIT_URL, self.DETAIL_URL, self.DELETE_URL)
        for name in self.urls_tuple:
            with self.subTest(name=name):
                response = self.reader_client.get(name)
                if name not in not_avaible:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertEqual(response.status_code,
                                     HTTPStatus.NOT_FOUND)
    
    def test_pages_availability_for_anonymous_client(self):
        not_avaible = (self.DETAIL_URL, self.EDIT_URL, self.DELETE_URL,
                       self.LIST_URL, self.SUCCESS_URL, self.ADD_URL)
        for name in self.urls_tuple:
            with self.subTest(name=name):
                redirect_url = f'{self.LOGIN_URL}?next={name}'
                response = self.client.get(name)
                if name not in not_avaible:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertRedirects(response, redirect_url)
