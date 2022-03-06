
import asyncio, time
import Byond, Shared
import common

async def do_test(env):
    env = env.branch()
    await compile(env)
    env = env.branch()
    await run(env)

async def compile(env):
    env.attr.process.log_mode = None
    env.attr.process.log_path = env.attr.test.base_dir / 'compile.log'
    env.attr.byond.compilation.file_path = env.attr.test.dm_file_path
    env.attr.byond.compilation.args = {}
    await Byond.Compilation.compile(env)

async def run(env):
    env.attr.process.log_mode = None
    env.attr.process.log_path = env.attr.test.base_dir / 'run.log'
    env.attr.byond.run.dm_file = Byond.Install.get_bytecode_file(env.attr.test.dm_file_path)
    env.attr.byond.run.args = {'trusted':True}
    await Byond.Run.run(env)
