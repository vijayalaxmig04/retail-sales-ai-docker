from app import app

app.config['TESTING'] = True

def test_login_page_loads(client):
    resp = client.get('/login')
    assert resp.status_code == 200
    assert b"Login" in resp.data

def test_dashboard_requires_login(client):
    resp = client.get('/dashboard', follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert '/login' in resp.headers.get('Location', '')

def test_invalid_login(client):
    resp = client.post('/login', data={'username': 'bad', 'password': 'bad'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Invalid credentials" in resp.data

def test_valid_login_and_dashboard(client):
    resp = client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Total Records" in resp.data

def test_predict_api_missing_payload(client):
    resp = client.post('/predict', json={})
    assert resp.status_code == 400 or resp.status_code == 200

if __name__ == '__main__':
    with app.test_client() as client:
        print('Testing login page...')
        assert client.get('/login').status_code == 200

        print('Testing protected dashboard redirect...')
        r = client.get('/dashboard')
        assert r.status_code in (302, 307)

        print('Testing invalid login...')
        r = client.post('/login', data={'username': 'bad', 'password': 'bad'}, follow_redirects=True)
        assert b'Invalid credentials' in r.data

        print('Testing valid login...')
        r = client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        assert r.status_code == 200
        assert b'Total Records' in r.data

        print('Testing predict API with missing payload...')
        r = client.post('/predict', json={})
        assert r.status_code in (400, 200)

        print('All tests passed!')
