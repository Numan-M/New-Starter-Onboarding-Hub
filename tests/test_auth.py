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
