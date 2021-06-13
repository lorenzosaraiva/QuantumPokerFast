from users import Users
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from urllib.error import HTTPError



class Auth:

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


    def __init__(self, users):
        self.users = users

    def fake_hash_password(self, password: str):
        return "fakehashed" + password

        
    def fake_decode_token(self, token):
        return self.users.get_user(token)
        


    async def get_current_user(self, token: str = Depends(oauth2_scheme)):
        user = self.fake_decode_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    async def login(self, username, password):
        print(username)
        user = self.users.get_user(username)
        print(user)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        hashed_password = self.fake_hash_password(password)
        if not hashed_password == user["hashed_password"]:
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        return {"access_token": user["username"], "token_type": "bearer"}
