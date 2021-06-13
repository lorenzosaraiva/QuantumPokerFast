from player import Player
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from table import Table
from game import Game
import pydantic
from typing import Optional
from pydantic import BaseModel
from urllib.error import HTTPError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger
import logging

gunicorn_logger = logging.getLogger('gunicorn.error')
logger.handlers = gunicorn_logger.handlers
logger.setLevel(logging.DEBUG)

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

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    player: Optional[str]= None

    class Config:
        arbitrary_types_allowed = True

    def get_table(self):
        if self.player:
            return self.player.table
        else:
            return None

class UserInDB(User):
    hashed_password: str
    
fake_users_db = {
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
}
def fake_hash_password(password: str):
    return "fakehashed" + password
app.mount("/public", StaticFiles(directory="public"), name="public")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



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



@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

game = Game()

@app.get("/")
async def root():
    return {"message": "Quantum poker"}

@app.get("/table_list")
async def get_table_list():
    return game.get_list()

async def get_table(f, current_user: User = Depends(get_current_user)):
    table = current_user.get_table()
    if table:
        return f(table)
    else:
        raise HTTPException(status_code=200, detail="Player not in table")
        
@app.get("/player")
async def showplayer(current_user: User = Depends(get_current_user)):
    return get_table(lambda table: table.all_players[current_user.player.id].serialize(), current_user)

@app.get("/table")
async def showtable(current_user: User = Depends(get_current_user)):
    return get_table(lambda table: table.serialize(), current_user)

@app.get("/find_table")
async def find_table(current_user: User = Depends(get_current_user)):
    return game.find_table(current_user).serialize()


@app.get("/check")
async def check(current_user: User = Depends(get_current_user)):
    table = current_user.get_table()
    if table:
        return table.check(current_user.player.id)
    else: 
        return "Not in table"

@app.get("/call")
async def call(current_user: User = Depends(get_current_user)):
    return get_table(lambda table: table.call(current_user.player.id), current_user)

@app.get("/fold")
async def fold(current_user: User = Depends(get_current_user)):
    return get_table(lambda table: table.fold(current_user.player.id), current_user)

#async def raise_bet( amount:int, current_user: User = Depends(get_current_user)):

@app.get("/raise_bet")
async def raise_bet(current_user: User = Depends(get_current_user)):
    return get_table(lambda table: table.raise_bet(current_user.player.id), current_user)

@app.get("/quantum_draw1")
async def quantum_draw1(current_user: User = Depends(get_current_user)):
    return get_table(lambda table: table.quantum_draw1(current_user.player.id), current_user)

@app.get("/quantum_draw2")
async def quantum_draw2(current_user: User = Depends(get_current_user)):
    return get_table(lambda table: table.quantum_draw2(current_user.player.id), current_user)

@app.get("/entangle1")
async def entangle1(current_user: User = Depends(get_current_user)):
    return get_table(lambda table: table.entangle_same_card1(current_user.player.id), current_user)

@app.get("/entangle2")
async def entangle2(current_user: User = Depends(get_current_user)):
    return get_table(lambda table: table.entangle_same_card2(current_user.player.id), current_user)

@app.get("/entangle_diff_1_2")
async def entangle_diff_1_2(current_user: User = Depends(get_current_user)):
    return get_table(lambda table: table.entangle_diff_1_2(current_user.player.id), current_user)

@app.get("/entangle_diff_2_1")
async def entangle_diff_2_1(current_user: User = Depends(get_current_user)):
    return get_table(lambda table: table.entangle_diff_2_1(current_user.player.id), current_user)

@app.get("/restart_hand/")
async def restart_hand(current_user: User = Depends(get_current_user)):
    return get_table(lambda table: table.restart_hand(), current_user)

@app.get("/top_up")
async def top_up(current_user: User = Depends(get_current_user)):
    return get_table(lambda table: table.top_up(current_user.player.id), current_user)
