
from common import *

env = setup()

async def tests():
    env.attr.clopendream.install.dir = env.attr.dirs.output / 'clopendream-repo'
    DMTestRunner.Dotnet.load_clopendream(env)
    import ClopenDream

    return

asyncio.run( tests() )