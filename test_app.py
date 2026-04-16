import pytest
from app import app, SECTIONS, ACCESS_SECTIONS

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret'
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['completed'] = []
        yield client


def test_home_redirect(client):
    response = client.get('/')
    assert response.status_code == 302
    assert SECTIONS[0] in response.location


def test_general_section_loads(client):
    response = client.get(f'/general/{SECTIONS[0]}')
    assert response.status_code == 200


def test_access_section_loads(client):
    response = client.get(f'/access/{ACCESS_SECTIONS[0]}')
    assert response.status_code == 200


def test_complete_item(client):
    item = SECTIONS[0]

    client.get(f'/complete/{item}')

    with client.session_transaction() as sess:
        assert item in sess['completed']


def test_no_duplicate_completion(client):
    item = SECTIONS[0]

    client.get(f'/complete/{item}')
    client.get(f'/complete/{item}')

    with client.session_transaction() as sess:
        assert sess['completed'].count(item) == 1


def test_undo_item(client):
    item = SECTIONS[0]

    client.get(f'/complete/{item}')
    client.get(f'/undo/{item}')

    with client.session_transaction() as sess:
        assert item not in sess['completed']


def test_render_page_contains_data(client):
    response = client.get(f'/general/{SECTIONS[0]}')

    assert response.status_code == 200
    assert b"Placeholder" in response.data