
from common import *

env = Shared.Environment()

load_config(env)
load_dotnet(env)

from DMCompiler import *
from System import *
import System.Threading.Tasks
import System.IO
from System.Collections.Generic import List
from Content.Tests import DMTests
from Robust.Shared.IoC import IoCManager
from OpenDreamRuntime import IDreamManager