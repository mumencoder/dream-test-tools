
from common import *

async def main():
    config = open_config()
    print_env(genv, "1")
    load_config(genv, config)
    print_env(genv, "2")

asyncio.run( main() )