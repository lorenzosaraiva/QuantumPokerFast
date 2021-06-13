from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_read_main():
    alive = client.get("/")
    assert alive.status_code == 200
    #testar /me sem login
    assert alive.json() == {'message': 'Quantum poker'}

    # John logs in
    login = client.post("/token", {'username':'johndoe', 'password':'secret'})
    assert login.status_code == 200
    login = login.json()
    assert login['access_token'] == 'johndoe'
    assert login['token_type'] == 'bearer'
    auth_john = {"Authorization":login['token_type']  + " " + login['access_token']}
    me = client.get("/users/me", headers=auth_john)
    assert me.status_code == 200
    me = me.json()
    assert me['username'] == "johndoe"
    assert me['email'] == "johndoe@example.com"
    assert me['full_name'] == "John Doe"
    assert me['disabled'] == False
    assert me['hashed_password'] == "fakehashedsecret"

    # Alice logs in
    login = client.post("/token", {'username':'alice', 'password':'secret2'})
    assert login.status_code == 200
    login = login.json()
    assert login['access_token'] == 'alice'
    assert login['token_type'] == 'bearer'
    auth_alice = {"Authorization":login['token_type']  + " " + login['access_token']}
    me = client.get("/users/me", headers=auth_alice)
    assert me.status_code == 200
    me = me.json()
    assert me['username'] == "alice"
    assert me['hashed_password'] == "fakehashedsecret2"



    # John tries to find a table
    find_table = client.get("/find_table", headers=auth_john)
    assert find_table.status_code == 200

    check = client.get("/check", headers=auth_john)
    assert check.status_code == 200


def test_read_main_alt():
    return
    alive = client.get("/")
    assert alive.status_code == 200
    #testar /me sem login
    assert alive.json() == {'message': 'Quantum poker'}

    # John logs in
    login = client.post("/token", {'username':'johndoe', 'password':'secret'})
    assert login.status_code == 200
    login = login.json()
    assert login['access_token'] == 'johndoe'
    assert login['token_type'] == 'bearer'
    auth_john = {"Authorization":login['token_type']  + " " + login['access_token']}
    me = client.get("/users/me", headers=auth_john)
    assert me.status_code == 200
    me = me.json()
    assert me['username'] == "johndoe"
    assert me['email'] == "johndoe@example.com"
    assert me['full_name'] == "John Doe"
    assert me['disabled'] == False
    assert me['player_id'] == 0
    assert me['hashed_password'] == "fakehashedsecret"

    # Alice logs in
    login = client.post("/token", {'username':'alice', 'password':'secret2'})
    assert login.status_code == 200
    login = login.json()
    assert login['access_token'] == 'alice'
    assert login['token_type'] == 'bearer'
    auth_alice = {"Authorization":login['token_type']  + " " + login['access_token']}
    me = client.get("/users/me", headers=auth_alice)
    assert me.status_code == 200
    me = me.json()
    assert me['username'] == "alice"
    assert me['player_id'] == 1
    assert me['hashed_password'] == "fakehashedsecret2"



    # John tries to find a table
    find_table = client.get("/find_table", headers=auth_john)
    assert find_table.status_code == 200

    # Alice player tries to find a table
    find_table = client.get("/find_table", headers=auth_alice)
    assert find_table.status_code == 200
    find_table = find_table.json()

    # They should be both in the same table
    assert len(find_table['all_players']) == 2

    #Bob logs in
    login = client.post("/token", {'username':'bob', 'password':'secret3'})
    assert login.status_code == 200
    login = login.json()
    assert login['access_token'] == 'bob'
    assert login['token_type'] == 'bearer'
    auth_bob = {"Authorization":login['token_type']  + " " + login['access_token']}
    me = client.get("/users/me", headers=auth_bob)
    assert me.status_code == 200
    me = me.json()
    assert me['username'] == "bob"
    assert me['hashed_password'] == "fakehashedsecret3"




    # A third player tries to find a table
    find_table = client.get("/find_table", headers=auth_bob)
    assert find_table.status_code == 200
    find_table = find_table.json()

    # He should be alone in his table
    assert len(find_table['all_players']) == 1
    
    # Getting the list of all tables
    table_list = client.get("/table_list", headers=auth_bob)
    assert table_list.status_code == 200
    table_list = table_list.json()

    # Should have 2 tables
    assert len(table_list) == 2


