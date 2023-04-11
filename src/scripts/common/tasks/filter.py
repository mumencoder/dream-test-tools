
from ..imports import *

async def filter_unknown_error(env):
    for error in env.attr.benv.attr.compile.stdout_parsed["errors"]:
        if error["category"] == "UNKNOWN":
            return True
    return False

async def filter_byond_compile_error(env):
    if env.attr.byond.compile.returncode != 0:
        return True
    return False

async def filter_compile_mispredict(env):
    if (env.attr.byond.compile.returncode == 0) is not (env.attr.collider.compile_predict):
        return True
    return False

async def filter_byond_opendream_compile_rt_mismatch(env):
    return False