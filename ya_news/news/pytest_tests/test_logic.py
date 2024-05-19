from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_comment(client, DETAIL_URL, form_for_comment):
    url = reverse(DETAIL_URL[0], args=DETAIL_URL[1])
    comments_before = Comment.objects.count()
    client.post(url, data=form_for_comment)
    assert Comment.objects.count() == comments_before


def test_autorized_user_can_create_comment(
        not_author_client, not_author, news, form_for_comment, DETAIL_URL
):
    url = reverse(DETAIL_URL[0], args=DETAIL_URL[1])
    comments_before = Comment.objects.count()
    not_author_client.post(url, data=form_for_comment)
    comments_difference = Comment.objects.count() - comments_before
    assert comments_difference == 1
    comment = Comment.objects.get()
    assert comment.news == news
    assert comment.author == not_author
    assert comment.text == form_for_comment['text']


def test_comment_bad_words(not_author_client, DETAIL_URL, form_for_comment):
    url = reverse(DETAIL_URL[0], args=DETAIL_URL[1])
    form_for_comment['text'] = f'ты {BAD_WORDS[1]}'
    comments_before = Comment.objects.count()
    response = not_author_client.post(url, data=form_for_comment)
    comments_difference = Comment.objects.count() - comments_before
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert comments_difference == 0


def test_author_can_edit_own_comms(
        author_client, news, comment, form_for_edit_comment, EDIT_URL
):
    url = reverse(EDIT_URL[0], args=EDIT_URL[1])
    comments_before = Comment.objects.count()
    response = author_client.post(url, form_for_edit_comment)
    redirect_url = reverse('news:detail', args=(news.id,)) + '#comments'
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == comments_before
    edited_comment = Comment.objects.get()
    assert edited_comment.text == form_for_edit_comment['text']
    assert edited_comment.news == comment.news
    assert edited_comment.author == comment.author
    assert edited_comment.created == comment.created


def test_user_cant_edit_comment_of_another_user(
        not_author_client, comment, form_for_edit_comment, form_for_comment,
        EDIT_URL
):
    url = reverse(EDIT_URL[0], args=EDIT_URL[1])
    comments_before = Comment.objects.count()
    response = not_author_client.post(url, form_for_edit_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_before
    edited_comment = Comment.objects.get()
    assert edited_comment.text == form_for_comment['text']
    assert edited_comment.news == comment.news
    assert edited_comment.author == comment.author
    assert edited_comment.created == comment.created


def test_author_can_delete_own_comms(author_client, news, DELETE_URL):
    url = reverse(DELETE_URL[0], args=DELETE_URL[1])
    comments_before = Comment.objects.count()
    response = author_client.post(url)
    redirect_url = reverse('news:detail', args=(news.id,)) + '#comments'
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() - comments_before == -1


def test_user_cant_delete_comment_of_another_user(
        not_author_client, DELETE_URL
):
    url = reverse(DELETE_URL[0], args=DELETE_URL[1])
    comments_before = Comment.objects.count()
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_before
