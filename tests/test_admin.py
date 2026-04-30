from app import User


# Permissions
def test_admin_access_allowed(client):
    client.post('/login', data={
        'username': 'admin',
        'password': 'adminpass'
    })

    response = client.get('/admin')
    assert response.status_code == 200


def test_admin_access_denied(client):
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    })

    response = client.get('/admin', follow_redirects=True)
    assert response.status_code == 200
    assert b'User management' not in response.data


# Admin page
def test_admin_page_access_allowed(client):
    client.post('/login', data={
        'username': 'admin',
        'password': 'adminpass'
    })

    response = client.get('/admin')

    assert response.status_code == 200
    assert b'User' in response.data or b'Create' in response.data


def test_admin_page_access_denied(client):
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    })

    response = client.get('/admin', follow_redirects=True)

    assert response.status_code == 200
    assert b'Sign in' in response.data

def test_admin_back_to_home(client):
    client.post('/login', data={
        'username': 'admin',
        'password': 'adminpass'
    })

    response = client.get('/', follow_redirects=True)

    assert response.status_code == 200
    assert b'Welcome' in response.data


def test_admin_logout(client):
    client.post('/login', data={
        'username': 'admin',
        'password': 'adminpass'
    })

    response = client.get('/logout', follow_redirects=True)

    assert response.status_code == 200
    assert b'Sign in' in response.data


# Admin actions
def test_create_user(client):
    client.post('/login', data={
        'username': 'admin',
        'password': 'adminpass'
    })

    response = client.post('/admin/create', data={
        'username': 'newuser',
        'password': 'newpass',
        'is_admin': 'on'
    }, follow_redirects=True)

    assert b'created successfully' in response.data


def test_toggle_admin(client, app):
    client.post('/login', data={
        'username': 'admin',
        'password': 'adminpass'
    })

    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        user_id = user.id

    response = client.post(f'/admin/toggle/{user_id}', follow_redirects=True)
    assert b'Admin status updated' in response.data


def test_delete_user(client, app):
    client.post('/login', data={
        'username': 'admin',
        'password': 'adminpass'
    })

    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        user_id = user.id

    response = client.post(f'/admin/delete/{user_id}', follow_redirects=True)
    assert b'deleted' in response.data