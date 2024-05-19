from django.conf import settings
from django.urls import reverse
import pytest

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('news_on_homepage')
def test_num_of_news_on_homepage(client, home_url):
    url = reverse(home_url[0])
    response = client.get(url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('news_on_homepage')
def test_ordering_news(client, home_url):
    url = reverse(home_url[0])
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.usefixtures('comments_for_news')
def test_ordering_comments(news):
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, detail_url):
    url = reverse(detail_url[0], args=detail_url[1])
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(not_author_client, detail_url):
    url = reverse(detail_url[0], args=detail_url[1])
    response = not_author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
