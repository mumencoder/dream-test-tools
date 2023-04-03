
from ..imports import *

async def filter_unknown_error(env):
    for error in env.attr.benv.attr.compile.stdout_parsed["errors"]:
        if error["category"] == "UNKNOWN":
            return True
        
async def filter_compile_failure(env):
    pass

async def filter_byond_opendream_match(env):
    pass

async def filter_compile_failure(env):
    pass