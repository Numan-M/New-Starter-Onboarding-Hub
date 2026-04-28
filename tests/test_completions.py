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