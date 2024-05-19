from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'URL, CLIENT, status_code',
    (
        (
            pytest.lazy_fixture('home_url'), pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('detail_url'), pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('login_url'), pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('logout_url'), pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('signup_url'), pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('edit_url'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('delete_url'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('delete_url'),
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
    'name',
    (pytest.lazy_fixture('edit_url'), pytest.lazy_fixture('delete_url'),)
)
def test_redirects(client, name, login_url):
    login_url = reverse(login_url[0])
    url = reverse(name[0], args=name[1])
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
