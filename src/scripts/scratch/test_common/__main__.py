
from common import *

async def main():
    root_env = base_env(verbose=True)
    await dmsource_all_tasks(root_env, verbose=True)

asyncio.run( main() )
