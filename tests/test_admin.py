from app import User, app



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
    assert b'Onboarding' in response.data

# Admin actions
def test_admin_page_access_allowed(client):
    client.post('/login', data={
        'username': 'admin',
        'password': 'adminpass'
    })

    response = client.get('/admin')

    assert response.status_code == 200
    assert b'User management' in response.data or b'Create new user' in response.data

def test_admin_page_access_denied(client):
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    })

    response = client.get('/admin', follow_redirects=True)

    # should redirect to home, not show admin content
    assert response.status_code == 200
    assert b'User management' not in response.data

def test_admin_back_to_home(client):
    # login as admin
    client.post('/login', data={
        'username': 'admin',
        'password': 'adminpass'
    })

    # go to admin page first
    client.get('/admin')

    # simulate clicking "back" button
    response = client.get('/', follow_redirects=True)

    assert response.status_code == 200
    assert b'Welcome' in response.data  # or another onboarding page check


def test_admin_logout(client):
    # login as admin
    client.post('/login', data={
        'username': 'admin',
        'password': 'adminpass'
    })

    # ensure we're logged in by hitting admin
    client.get('/admin')

    # click logout
    response = client.get('/logout', follow_redirects=True)

    assert response.status_code == 200
    assert b'Sign in' in response.data  # your login page text
    
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

def test_toggle_admin(client):
    client.post('/login', data={
        'username': 'admin',
        'password': 'adminpass'
    })

    with app.app_context():
        user = User.query.filter_by(username='testuser').first()

    response = client.post(f'/admin/toggle/{user.id}', follow_redirects=True)
    assert b'Admin status updated' in response.data

def test_delete_user(client):
    client.post('/login', data={
        'username': 'admin',
        'password': 'adminpass'
    })

    user = User.query.filter_by(username='testuser').first()

    response = client.post(f'/admin/delete/{user.id}', follow_redirects=True)
    assert b'deleted' in response.data