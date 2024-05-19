from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects

import pdb
@pytest.mark.django_db
@pytest.mark.parametrize(
    'URL, CLIENT, status_code',
    (
        (
            pytest.lazy_fixture('HOME_URL'), pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('DETAIL_URL'), pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('LOGIN_URL'), pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('LOGOUT_URL'), pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('SIGNUP_URL'), pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('EDIT_URL'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('DELETE_URL'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('DELETE_URL'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('DELETE_URL'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
    )
)
def test_pages_avaibility(URL, CLIENT, status_code):
    url = reverse(URL[0], args=URL[1])
    response = CLIENT.get(url)
    assert response.status_code == status_code

@pytest.mark.parametrize(
    'URL',
    (pytest.lazy_fixture('EDIT_URL'), pytest.lazy_fixture('DELETE_URL'),)
)
def test_redirects(client, URL, LOGIN_URL):
    login_url = reverse(LOGIN_URL[0])
    url = reverse(URL[0], args=URL[1])
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
