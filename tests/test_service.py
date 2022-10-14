import pytest

@pytest.fixture()
def client(app):
    return app.test_client()

def test_user_creation(client):
    response = client.post("/users")
    assert 'id' in response.json
    get_response = client.get("/users", query_string={"id": response.json['id']})
    print(get_response.status)
    assert 'id' in get_response.json
    assert response.json['id'] == get_response.json['id']

def test_user_error(client):
    response = client.post("/users")
    get_response = client.get("/users", query_string={"other_param": response.json['id']})
    print(get_response.json)
    assert get_response.status_code == 400
    get_response = client.get("/users", query_string={"id": response.json['id']+1})
    assert get_response.status_code == 404

def test_create_game(client):
    response = client.post("/games")
    assert response.status_code == 200
    g = response.json
    assert g['board'] == [
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
    ]
    assert g['players'] == []
    assert g['status'] == 'pending_players'
    assert g['results'] == []

def test_get_invalid_game(client):
    response = client.post("/games")
    get_response = client.get(f"/games/{response.json['id']+1}")
    assert get_response.status_code == 404

def test_join_game(client):
    user = client.post("/users")
    response = client.post("/games")
    join_response = client.post(f"/games/{response.json['id']}/join", data={"user_id" : user.json['id']})
    assert join_response.status_code == 200
    # Joining again should be a failure
    join_again_response = client.post(f"/games/{response.json['id']}/join", data={"user_id" : user.json['id']})
    assert join_again_response.status_code == 400
    # Another user joins
    other_user = client.post("/users")
    other_join_response = client.post(f"/games/{response.json['id']}/join", data={"user_id" : other_user.json['id']})
    assert other_join_response.status_code == 200
    assert other_join_response.json['status'] == 'in_progress'

def test_play_game(client):
    user = client.post("/users")
    other_user = client.post("/users")
    game = client.post("/games")
    client.post(f"/games/{game.json['id']}/join", data={"user_id" : user.json['id']})
    r = client.post(f"/games/{game.json['id']}/join", data={"user_id" : other_user.json['id']})
    assert r.json['status'] == 'in_progress'
    # Make a move
    move_response = client.post(f"/games/{game.json['id']}/move", data={
        "user_id" : user.json['id'],
        "row" : 0, 
        "column" : 0,
    })
    print(move_response.text)

    assert move_response.status_code == 200
    assert move_response.json['board'] == [
        ["X", "", ""],
        ["", "", ""],
        ["", "", ""],
    ]