
from common import *

async def opendream():
    env = base_env()
    
    DMShared.OpenDream.Install.load_repo(env, env.attr.config.attr.opendream_main )
    await DMShared.OpenDream.Install.init_repo(env)
    DMShared.OpenDream.Install.load_install_from_repo(env)
    await DMShared.OpenDream.Builder.build(env)

try:
    asyncio.run( globals()[sys.argv[1]]() )
except KeyboardInterrupt:
    pass