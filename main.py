from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import logging
from game import Game
from users import Users
from auth import Auth
from user import User



gunicorn_logger = logging.getLogger('gunicorn.error')
logger.handlers = gunicorn_logger.handlers
logger.setLevel(logging.DEBUG)

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://quantum-poker-react.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

users = Users()
auth = Auth(users)



app.mount("/public", StaticFiles(directory="public"), name="public")


@app.post("/token")
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    return await auth.login(form_data.username, form_data.password)


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(auth.get_current_user)):
    return current_user

game = Game()


@app.get("/")
async def root():
    return {"message": "Quantum poker"}

@app.get("/table_list")
async def get_table_list():
    return game.get_list()

async def get_table(f, current_user: User = Depends(auth.get_current_user)):
    table = game.get_table(current_user["username"])
    if table:
        return f(table)
    #else:
        #raise HTTPException(status_code=200, detail="Player not in table")
        
@app.get("/player")
async def show_player(current_user: User = Depends(auth.get_current_user)):
    return game.get_player(current_user["username"])


@app.get("/table")
async def show_table(current_user: User = Depends(auth.get_current_user)):
    return await get_table(lambda table: table.serialize(), current_user)

@app.get("/find_table")
async def find_table(current_user: User = Depends(auth.get_current_user)):
    return game.find_or_create_table(current_user["username"])


@app.get("/check")
async def check(current_user: User = Depends(auth.get_current_user)):
    return await get_table(lambda table: table.check(current_user["username"]), current_user)


@app.get("/call")
async def call(current_user: User = Depends(auth.get_current_user)):
    return await get_table(lambda table: table.call(current_user["username"]), current_user)

@app.get("/fold")
async def fold(current_user: User = Depends(auth.get_current_user)):
    return await get_table(lambda table: table.fold(current_user["username"]), current_user)

#async def raise_bet( amount:int, current_user: User = Depends(auth.get_current_user)):

@app.get("/raise_bet")
async def raise_bet(amount:int, current_user: User = Depends(auth.get_current_user)):
    return await get_table(lambda table: table.raise_bet(current_user["username"], amount), current_user)

@app.get("/quantum_draw1")
async def quantum_draw1(current_user: User = Depends(auth.get_current_user)):
    return await get_table(lambda table: table.quantum_draw1(current_user["username"]), current_user)

@app.get("/quantum_draw2")
async def quantum_draw2(current_user: User = Depends(auth.get_current_user)):
    return await get_table(lambda table: table.quantum_draw2(current_user["username"]), current_user)

@app.get("/entangle1")
async def entangle1(current_user: User = Depends(auth.get_current_user)):
    return await get_table(lambda table: table.entangle_same_card1(current_user["username"]), current_user)

@app.get("/entangle2")
async def entangle2(current_user: User = Depends(auth.get_current_user)):
    return await get_table(lambda table: table.entangle_same_card2(current_user["username"]), current_user)

@app.get("/entangle_diff_1_2")
async def entangle_diff_1_2(current_user: User = Depends(auth.get_current_user)):
    return await get_table(lambda table: table.entangle_diff_1_2(current_user["username"]), current_user)

@app.get("/entangle_diff_2_1")
async def entangle_diff_2_1(current_user: User = Depends(auth.get_current_user)):
    return await get_table(lambda table: table.entangle_diff_2_1(current_user["username"]), current_user)

@app.get("/restart_hand/")
async def restart_hand(current_user: User = Depends(auth.get_current_user)):
    return await get_table(lambda table: table.restart_hand(), current_user)

@app.get("/top_up")
async def top_up(current_user: User = Depends(auth.get_current_user)):
    return await get_table(lambda table: table.top_up(current_user["username"]), current_user)
