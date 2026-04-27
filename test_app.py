import pytest
from app import app, db, User, Completion


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            # create a default user
            user = User(username="testuser", is_admin=False)
            user.set_password("password")
            db.session.add(user)

            # admin user
            admin = User(username="admin", is_admin=True)
            admin.set_password("adminpass")
            db.session.add(admin)

            db.session.commit()

        yield client

        with app.app_context():
            db.drop_all()


# Login features
def test_login_success(client):
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Welcome' in response.data or b'Onboarding' in response.data

def test_login_failure(client):
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpassword'
    })

    assert b'Incorrect username or password' in response.data

def test_logout(client):
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    })

    response = client.get('/logout', follow_redirects=True)
    assert b'Sign in' in response.data

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

# Completion tracking
def test_complete_section(client):
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    })

    response = client.get('/complete/Welcome', follow_redirects=True)

    assert response.status_code == 200

def test_undo_section(client):
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    })

    client.get('/complete/Welcome')
    response = client.get('/undo/Welcome', follow_redirects=True)

    assert response.status_code == 200

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

# Sections
# Sections (sidebar navigation routes)
@pytest.mark.parametrize("route, expected_status", [
    ("/general/Welcome", 200),
    ("/general/Training", 200),
    ("/general/Authentication", 200),
    ("/general/Equipment", 200),
    ("/general/Information sources", 200),
    ("/general/Organisation structure", 200),
    ("/general/myHR", 200),
    ("/general/Employee benefits", 200),

    ("/access/Jira", 200),
    ("/access/Confluence", 200),
    ("/access/Figma", 200),
    ("/access/ServiceNow", 200),
    ("/access/Service accounts", 200),
    ("/access/Developer folders", 200),
    ("/access/Developer tools", 200),
])
def test_sidebar_routes(client, route, expected_status):
    # login first (required for all pages)
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    })

    response = client.get(route, follow_redirects=True)

    assert response.status_code == expected_status