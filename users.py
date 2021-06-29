
from user import User


class Users():

    def __init__(self):
    
        self.db = {
            "johndoe": {
                "username": "johndoe",
                "full_name": "John Doe",
                "email": "johndoe@example.com",
                "hashed_password": "fakehashedsecret",
                "disabled": False,
            },
            "alice": {
                "username": "alice",
                "full_name": "Alice Wonderson",
                "email": "alice@example.com",
                "hashed_password": "fakehashedsecret2",
                "disabled": True,
            },
            "bob": {
                "username": "bob",
                "full_name": "bob classes",
                "email": "bob@example.com",
                "hashed_password": "fakehashedsecret3",
                "disabled": True,
            }, 
            "carl": {
                "username": "carl",
                "full_name": "carl larc",
                "email": "carl@example.com",
                "hashed_password": "fakehashedsecret4",
                "disabled": True,
            }, 
        }

    def get_user(self, username: str):
        if username in self.db:
            return self.db[username]
        else:
            return None

