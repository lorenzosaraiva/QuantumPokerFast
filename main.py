from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from table import Table

app = FastAPI()
app.mount("/public", StaticFiles(directory="public"), name="public")

table = Table()

@app.get("/")
async def root():
    return {"message": "Quantum poker"}

@app.get("/player/{player_id}")
async def showplayer(player_id:int):
    return table.all_players[player_id].serialize()

@app.get("/table")
async def showtable():
    return table.serialize()

@app.get("/check/{player_id}")
async def check(player_id:int):
    return table.check(player_id)

@app.get("/call/{player_id}")
async def call(player_id:int):
    return table.call(player_id)

@app.get("/fold/{player_id}")
async def fold(player_id:int):
    return table.fold(player_id)

@app.get("/raise_bet/{player_id}/{amount}")
async def raise_bet(player_id:int, amount:int):
    return table.raise_bet(player_id, amount)

@app.get("/quantum_draw1/{player_id}")
async def quantum_draw1(player_id:int):
    return table.quantum_draw1(player_id)

@app.get("/quantum_draw2/{player_id}")
async def quantum_draw2(player_id:int):
    return table.quantum_draw2(player_id)

@app.get("/restart_hand/")
async def restart_hand():
    return table.restart_hand()
