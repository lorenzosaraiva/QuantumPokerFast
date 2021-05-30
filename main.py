from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from table import Table
import pydantic
from typing import Optional
from pydantic import BaseModel
from urllib.error import HTTPError
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "player_id": 0,
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "player_id": 1,
        "disabled": True,
    },
}
def fake_hash_password(password: str):
    return "fakehashed" + password



app.mount("/public", StaticFiles(directory="public"), name="public")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

table = Table(2)

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    player_id: Optional[int] = None

class UserInDB(User):
    hashed_password: str
    
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}



async def get_current_active_user(v):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}

@app.get("/")
async def root():
    return {"message": "Quantum poker"}
    
@app.get("/player")
async def showplayer(current_user: User = Depends(get_current_user)):
    return table.all_players[current_user.player_id].serialize()

@app.get("/table")
async def showtable():
    return table.serialize()

@app.get("/check")
async def check(current_user: User = Depends(get_current_user)):
    return table.check(current_user.player_id)

@app.get("/call")
async def call(current_user: User = Depends(get_current_user)):
    return table.call(current_user.player_id)

@app.get("/fold")
async def fold(current_user: User = Depends(get_current_user)):
    return table.fold(current_user.player_id)

@app.get("/raise_bet/{amount}")
async def raise_bet( amount:int, current_user: User = Depends(get_current_user)):
    return table.raise_bet(current_user.player_id, amount)

@app.get("/quantum_draw1")
async def quantum_draw1(current_user: User = Depends(get_current_user)):
    return table.quantum_draw1(current_user.player_id)

@app.get("/quantum_draw2")
async def quantum_draw2(current_user: User = Depends(get_current_user)):
    return table.quantum_draw2(current_user.player_id)

@app.get("/entangle1")
async def entangle1(current_user: User = Depends(get_current_user)):
    return table.entangle_same_card1(current_user.player_id)

@app.get("/entangle2")
async def entangle2(current_user: User = Depends(get_current_user)):
    return table.entangle_same_card2(current_user.player_id)

@app.get("/entangle_diff_1_2")
async def entangle_diff_1_2(current_user: User = Depends(get_current_user)):
    return table.entangle_diff_1_2(current_user.player_id)

@app.get("/entangle_diff_2_1")
async def entangle_diff_2_1(current_user: User = Depends(get_current_user)):
    return table.entangle_diff_2_1(current_user.player_id)

@app.get("/restart_hand/")
async def restart_hand():
    return table.restart_hand()

@app.get("/top_up")
async def top_up(current_user: User = Depends(get_current_user)):
    return table.top_up(current_user.player_id)
