from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

HOME_URL = pytest.lazy_fixture('home_url')

DETAIL_URL = pytest.lazy_fixture('detail_url')

EDIT_URL = pytest.lazy_fixture('edit_url')

DELETE_URL = pytest.lazy_fixture('delete_url')

LOGIN_URL = pytest.lazy_fixture('login_url')

LOGOUT_URL = pytest.lazy_fixture('logout_url')

SIGNUP_URL = pytest.lazy_fixture('signup_url')

CLIENT = pytest.lazy_fixture('client')

AUTHOR_CLIENT = pytest.lazy_fixture('author_client')

NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, user, status_code',
    (
        (HOME_URL, CLIENT, HTTPStatus.OK),
        (DETAIL_URL, CLIENT, HTTPStatus.OK),
        (LOGIN_URL, CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, CLIENT, HTTPStatus.OK),
        (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
    )
)
def test_pages_avaibility(name, user, status_code):
    url = name
    response = user.get(url)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    'name',
    (EDIT_URL, DELETE_URL)
)
def test_redirects(client, name, login_url):
    url = name
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
