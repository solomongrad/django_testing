from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

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


    def test_notes_list_for_different_users(self):
        for user, note_in_list in ((self.author, True), (self.reader, False)):
            with self.subTest(user=user):
                self.client.force_login(user)
                url = reverse('notes:list')
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertEqual((self.note in object_list), note_in_list)


    def test_pages_contains_form(self):
        self.client.force_login(self.author)
        for name, args in (('notes:add', None), ('notes:edit', (self.note.slug,))):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
