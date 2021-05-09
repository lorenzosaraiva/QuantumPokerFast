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
    return table.players[player_id]

@app.get("/table")
async def showtable():
    return table

@app.get("/check")
async def check():
    return table.check()
