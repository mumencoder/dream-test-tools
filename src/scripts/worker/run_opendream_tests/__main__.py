
from common import *

root_env = base_env()
load_config( root_env, sys.argv[1], sys.argv[2] )

async def opendream_test(oenv, tenv):
    test_result = {}

    reset_test(tenv)

    cenv = oenv.branch()
    cenv.attr.compilation.root_dir = tenv.attr.test.base_dir
    cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
    await DMShared.OpenDream.Compilation.managed_compile(cenv)
    test_result['source'] = tenv.attr.test.text
    test_result["compile.returncode"] = cenv.attr.compile.returncode
    test_result["compile.stdout"] = cenv.attr.compile.stdout 

    if cenv.attr.compile.returncode == 0:
        renv = oenv.branch()
        DMShared.OpenDream.Run.prepare_from_compilation(renv, cenv)
        await DMShared.OpenDream.Run.managed_run(renv)

        test_result["run.returncode"] = renv.attr.run.returncode
        test_result["run.stdout"] = renv.attr.run.stdout

        DMShared.DMSource.TestCase.load_result(tenv)
        test_result["run.run_out"] = tenv.attr.result.run_out
        test_result["run.run_unexpected_out"] = tenv.attr.result.run_unexpected_out
    return test_result

async def main():
    oenv = root_env.branch()
    oenv.attr.install.dir = root_env.attr.dirs.opendream_install
    oenv.attr.process.try_terminate = termination_check

    r_tenv = root_env.branch()
    r_tenv.attr.test.base_dir = root_env.attr.dirs.tmp / 'tests' / 'current'
    r_tenv.attr.results = {}

    results = {"install_id":root_env.attr.opendream.install_id, "tests":[]}
    start_time = time.time()

    run_id = f'{root_env.attr.byond.install_id}.{root_env.attr.tests.group_id}'
    for tenv in DMShared.DMSource.TestCase.iter_tests( r_tenv, root_env.attr.dirs.dm_tests ):
        print( tenv.attr.test.source_file )
        test_result = {"name": tenv.attr.test.source_file.stem }
        test_result["result"] = await opendream_test(oenv, tenv)
        results["tests"].append( test_result )
    print( time.time() - start_time )

    update_testrun(root_env, run_id, results)

asyncio.run( main() )