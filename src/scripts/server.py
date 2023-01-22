
from common import *

root_env = Shared.Environment()
setup_base(root_env)
load_config(root_env)
DMShared.PileArchive.load(root_env)

app = fastapi.FastAPI()

@app.post("/ast_gen")
async def root(request : fastapi.Request):
    env = root_env.branch()
    env.attr.pile.id = Shared.Random.generate_string(24)

    data = json.loads( gzip.decompress( await request.body() ) )
    for test in data["tests"]:
        test["id"] = Shared.Random.generate_string(24)

    env.attr.pile.data = data
    DMShared.PileArchive.Pile.save(env)