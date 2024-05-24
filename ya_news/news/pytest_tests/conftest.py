from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
import pytest

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(title='заголовок', text='просто текст',)


@pytest.fixture
def form_for_comment():
    return {'text': 'Текст комментария'}


@pytest.fixture
def form_for_edit_comment():
    return {'text': 'Новый текст комментария'}


@pytest.fixture
def comment(author, news, form_for_comment):
    return Comment.objects.create(
        news=news,
        author=author,
        text=form_for_comment['text'],
    )


@pytest.fixture
def news_on_homepage():
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comments_for_news(author, news):
    for index in range(11):
        Comment.objects.create(
            news=news,
            author=author,
            text=f'комментарий {index}',
        )


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')
