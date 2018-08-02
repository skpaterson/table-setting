import json
import pytest

from run_app import app, database

def setup_module():
    with app.test_request_context():
        database.drop_all()
        database.create_all()

def teardown_module():
    with app.test_request_context():
        database.drop_all()


@pytest.fixture
def client():
    return app.test_client()


def test_get_forks(client):
    resp = client.get('/forks')
    assert resp.status_code == 200
    assert len(json.loads(resp.data)) == 0


def test_create_read_delete_fork(client):
    resp = client.post('/forks', data=json.dumps({'name': 'forky', 'prongs': 8}), headers={'content-type': 'application/json'})
    assert resp.status_code == 201
    response_data = json.loads(resp.data)
    assert response_data['name'] == 'forky'
    assert response_data['prongs'] == 8
    # we now also have an ID
    fork_id = response_data['id']
    # check our fork is there
    resp = client.get('/forks')
    assert resp.status_code == 200
    assert len(json.loads(resp.data)) == 1
    # confirm we can get the fork using the ID
    resp = client.get('/forks/%s' %fork_id)
    assert resp.status_code == 200
    response_data = json.loads(resp.data)
    assert response_data['name'] == 'forky'
    assert response_data['prongs'] == 8
    assert response_data['id'] == fork_id
    # now delete our fork
    resp = client.delete('/forks/%s' %fork_id)
    assert resp.status_code == 204
    # confirm our fork is deleted
    resp = client.get('/forks')
    assert resp.status_code == 200
    assert len(json.loads(resp.data)) == 0


def test_create_update_delete_fork(client):
    resp = client.post('/forks', data=json.dumps({'name': 'forky2', 'prongs': 3}), headers={'content-type': 'application/json'})
    assert resp.status_code == 201
    response_data = json.loads(resp.data)
    assert response_data['name'] == 'forky2'
    assert response_data['prongs'] == 3
    fork_id = response_data['id']
    # now let's update our fork
    resp = client.put('/forks/%s' %fork_id, data=json.dumps({'name': 'forky2', 'prongs': 4}), headers={'content-type': 'application/json'})
    assert resp.status_code == 204
    assert resp.data == b''
    resp = client.get('/forks/%s' %fork_id)
    response_data = json.loads(resp.data)
    assert response_data['name'] == 'forky2'
    # ensure our prongs are correct
    assert response_data['prongs'] == 4
    resp = client.delete('/forks/%s' %fork_id)
    assert resp.status_code == 204


def test_create_multiple_forks(client):
    resp = client.post('/forks', data=json.dumps({'name': 'first fork', 'prongs': 100}), headers={'content-type': 'application/json'})
    assert resp.status_code == 201
    response_data = json.loads(resp.data)
    assert response_data['name'] == 'first fork'
    assert response_data['prongs'] == 100
    first_id = response_data['id']
    resp = client.post('/forks', data=json.dumps({'name': 'second fork', 'prongs': 50}), headers={'content-type': 'application/json'})
    assert resp.status_code == 201
    response_data = json.loads(resp.data)
    assert response_data['name'] == 'second fork'
    assert response_data['prongs'] == 50
    second_id = response_data['id']
    resp = client.get('/forks')
    assert resp.status_code == 200
    assert len(json.loads(resp.data)) == 2
    # now clean up
    resp = client.delete('/forks/%s' %first_id)
    assert resp.status_code == 204
    resp = client.delete('/forks/%s' %second_id)
    assert resp.status_code == 204