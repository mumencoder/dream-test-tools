
from ..common import *

class Dotnet:
    async def setup_opendream_dotnet():
        savedir = os.getcwd()
        os.chdir( str( Shared.Path( env.attr.collider.config["opendream"]["repo_dir"] ) / 'bin' / 'Content.Tests' / 'DMProject' ) )
        tests = DMTests()
        tests.BaseSetup()
        tests.OneTimeSetup()
        os.chdir( savedir )
        dreamman = IoCManager.Resolve[IDreamManager]()