from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNotesLogic(TestCase):

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
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        cls.SLUG = cls.note.slug
        cls.SUCCESS_URL = reverse('notes:success')
        cls.ADD_URL = reverse('notes:add')
        cls.LOGIN_URL = reverse('users:login')
        cls.DELETE_URL = reverse('notes:delete', args=(cls.SLUG,))

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)

    def test_user_can_create_note(self):
        url = self.ADD_URL
        Note.objects.all().delete()
        notes_before = Note.objects.count()
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual((Note.objects.count() - notes_before), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        url = self.ADD_URL
        Note.objects.all().delete()
        notes_before = Note.objects.count()
        response = self.client.post(url, data=self.form_data)
        login_url = self.LOGIN_URL
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), notes_before)

    def test_empty_slug(self):
        url = self.ADD_URL
        self.form_data.pop('slug')
        Note.objects.all().delete()
        notes_before = Note.objects.count()
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual((Note.objects.count() - notes_before), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_not_unique_slug(self):
        url = reverse('notes:add')
        self.form_data['slug'] = self.note.slug
        notes_before = Note.objects.count()
        response = self.author_client.post(url, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), notes_before)

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        self.assertEqual(Note.objects.count(), 1)
        response = self.author_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        edited_note = Note.objects.get()
        self.assertEqual(edited_note.title, self.form_data['title'])
        self.assertEqual(edited_note.text, self.form_data['text'])
        self.assertEqual(edited_note.slug, self.form_data['slug'])
        self.assertEqual(edited_note.author, self.author)

    def test_other_user_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        self.assertEqual(Note.objects.count(), 1)
        response = self.reader_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get()
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, self.author)

    def test_author_can_delete_note(self):
        url = self.DELETE_URL
        notes_before = Note.objects.count()
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual((notes_before - Note.objects.count()), 1)

    def test_other_user_cant_delete_note(self):
        url = self.DELETE_URL
        notes_before = Note.objects.count()
        response = self.reader_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_before, Note.objects.count())
