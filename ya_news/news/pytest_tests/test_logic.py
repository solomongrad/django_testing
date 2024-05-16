import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_comment(client, news, form_for_comment):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_for_comment)
    assert Comment.objects.count() == 0


def test_autorized_user_can_create_comment(
        not_author_client, not_author, news, form_for_comment
):
    url = reverse('news:detail', args=(news.id,))
    not_author_client.post(url, data=form_for_comment)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.news == news
    assert comment.author == not_author
    assert comment.text == form_for_comment['text']


def test_comment_bad_words(not_author_client, news, form_for_comment):
    url = reverse('news:detail', args=(news.id,))
    form_for_comment['text'] = f'ты {BAD_WORDS[1]}'
    response = not_author_client.post(url, data=form_for_comment)
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_own_comms(
        author_client, news, comment, form_for_edit_comment
):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, form_for_edit_comment)
    redirect_url = reverse('news:detail', args=(news.id,)) + '#comments'
    assertRedirects(response, redirect_url)
    comment.refresh_from_db()
    assert comment.text == form_for_edit_comment['text']


def test_user_cant_edit_comment_of_another_user(
        not_author_client, comment, form_for_edit_comment, form_for_comment
):
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, form_for_edit_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == form_for_comment['text']


def test_author_can_delete_own_comms(author_client, news, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    redirect_url = reverse('news:detail', args=(news.id,)) + '#comments'
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client, news, comment
):
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
