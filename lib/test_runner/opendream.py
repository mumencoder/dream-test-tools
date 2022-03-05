
import asyncio, time
import Shared, OpenDream
import common, test_runner

async def do_test(env):
    await compile(env)
    await run(env)

async def compile(env):
    env = env.branch()
    env.attr.opendream.compilation.dm_file = env.attr.test.dm_file_path
    env.attr.opendream.compilation.args = {}
    env.attr.wf.status.append("test.compile.opendream")
    await OpenDream.Compilation.compile(env)
    env.attr.wf.status.pop()

async def run(env):
    env = env.branch()
    env.attr.opendream.run.file = OpenDream.Run.get_bytecode_file(env.attr.test.dm_file_path)
    env.attr.opendream.run.args = {}
    env.event_handlers['process.wait'] = test_runner.wait_run_complete
    env.attr.wf.status.append("test.run.opendream")
    await OpenDream.Run.run(env)
    env.attr.wf.status.pop()
