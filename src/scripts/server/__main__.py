
import fastapi
import fastapi.security.api_key as apiseckey

from common import *

app = fastapi.FastAPI()

api_key_header = apiseckey.APIKeyHeader(name="x-auth-key", auto_error=False)
api_key_query = apiseckey.APIKeyQuery(name="auth", auto_error=False)

def check_api_key(
    api_key_query: str = fastapi.Security(api_key_query),
    api_key_header: str = fastapi.Security(api_key_header),
):
    if api_key_query in api_keys:
        return api_key_query
    if api_key_header in api_keys:
        return api_key_header
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )
    
@app.get("/home")
async def home(request : fastapi.Request, api_key = fastapi.Security(check_api_key)):
    pass

@app.post("/ast_gen")
async def ast_gen(request : fastapi.Request):
    env = root_env.branch()
    env.attr.pile.id = Shared.Random.generate_string(24)

    data = json.loads( gzip.decompress( await request.body() ) )
    for test in data["tests"]:
        test["id"] = Shared.Random.generate_string(24)

    env.attr.pile.data = data
    DMShared.PileArchive.Pile.save(env)
    