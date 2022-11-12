

from common import *

env = Shared.Environment()

load_config(env)
load_dotnet(env)

from dream_collider import *

from System import *
import System.IO
from System.Collections.Generic import List
import System.Threading.Tasks

import DMCompiler
import DMCompiler.Compiler.DM
from Content.Tests import DMTests
from Robust.Shared.IoC import IoCManager
from OpenDreamRuntime import IDreamManager


load_ast_types()