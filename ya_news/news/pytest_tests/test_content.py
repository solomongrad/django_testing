import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_num_of_news_on_homepage(client, posts_on_homepage):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_ordering_news(client, posts_on_homepage):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_ordering_comments(comments_for_post, news):
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(not_author_client, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    response = not_author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
