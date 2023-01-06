
from common import *

import fastapi
import redis
from redis.commands.json.path import Path

client = redis.Redis(host='localhost', port=6379, db=0)

app = fastapi.FastAPI()

@app.post("/ast_gen")
async def root(request : fastapi.Request):
    print( len( await request.body() ) )
 