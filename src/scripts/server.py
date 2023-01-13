
from common import *

import fastapi
import redis
from redis.commands.json.path import Path

config = load_config()

if os.path.exists( config["paths"]["piles"] ):
    shutil.rmtree( config["paths"]["piles"] )

client = redis.Redis(host='localhost', port=6379, db=0)

app = fastapi.FastAPI()

@app.post("/ast_gen")
async def root(request : fastapi.Request):
    pile_id = Shared.Random.generate_string(24)
    data = json.loads( gzip.decompress( await request.body() ) )
    for test in data["tests"]:
        test["id"] = Shared.Random.generate_string(24)

    with open( config["paths"]["piles"] / f"{pile_id}.json", "wb") as f:
        f.write( gzip.compress( json.dumps( data ).encode('ascii') ) )
