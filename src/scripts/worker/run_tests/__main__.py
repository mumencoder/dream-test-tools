
from common import *

root_env = base_env()
load_config( root_env, sys.argv[1] )

def reset_test(tenv):
    if os.path.exists( tenv.attr.test.base_dir ):
        shutil.rmtree( tenv.attr.test.base_dir )
    DMShared.DMSource.TestCase.load_test(tenv)
    DMShared.DMSource.TestCase.write(tenv)

async def byond_test(benv, tenv):
    test_result = {}

    reset_test(tenv)

    cenv = benv.branch()
    cenv.attr.compilation.root_dir = tenv.attr.test.base_dir
    cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
    await DMShared.Byond.Compilation.managed_compile(cenv)
    test_result['source'] = tenv.attr.test.text
    test_result["compile.returncode"] = cenv.attr.compile.returncode
    test_result["compile.stdout"] = cenv.attr.compile.stdout 

    if cenv.attr.compile.returncode == 0:
        renv = benv.branch()
        DMShared.Byond.Run.prepare_from_compilation(renv, cenv)
        await DMShared.Byond.Run.managed_run(renv)

        test_result["run.returncode"] = renv.attr.run.returncode
        test_result["run.stdout"] = renv.attr.run.stdout

        DMShared.DMSource.TestCase.load_result(tenv)
        test_result["run.run_out"] = tenv.attr.result.run_out
        test_result["run.run_unexpected_out"] = tenv.attr.result.run_unexpected_out
    return test_result

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

async def termination_check(env):
    if os.path.exists( os.path.join(env.attr.shell.dir, 'fin') ):
        return True
    elif Shared.Process.limited_process(env, time_limit=5.0, memory_limit=1*1024**3):
        return True
    return False

async def main():
    byond_version = list(sorted( os.listdir(root_env.attr.dirs.byond_install), reverse=True ))[0]

    benv = root_env.branch()
    benv.attr.install.dir = root_env.attr.dirs.byond_install / byond_version
    benv.attr.process.try_terminate = termination_check

    oenv = root_env.branch()
    oenv.attr.install.dir = root_env.attr.dirs.opendream_install
    oenv.attr.process.try_terminate = termination_check

    r_tenv = root_env.branch()
    r_tenv.attr.test.base_dir = root_env.attr.dirs.tmp / 'tests' / 'current'
    r_tenv.attr.results = {}

    results = {"install_id":"current_byond", "tests":[]}
    start_time = time.time()
    for tenv in DMShared.DMSource.TestCase.iter_tests( r_tenv, root_env.attr.dirs.dm_tests ):
        print( tenv.attr.test.source_file )
        test_result = {"name": tenv.attr.test.source_file.stem }
        test_result["result"] = await byond_test(benv, tenv)
        results["tests"].append( test_result )
    print( time.time() - start_time )
    with open( root_env.attr.dirs.testruns / 'current_byond.pickle', 'wb' ) as f:
        f.write( pickle.dumps(results) ) 

    results = {"install_id":"current_opendream", "tests":[]}
    start_time = time.time()
    for tenv in DMShared.DMSource.TestCase.iter_tests( r_tenv, root_env.attr.dirs.dm_tests ):
        print( tenv.attr.test.source_file )
        test_result = {"name": tenv.attr.test.source_file.stem }
        test_result["result"] = await opendream_test(oenv, tenv)
        results["tests"].append( test_result )
    print( time.time() - start_time )
    with open( root_env.attr.dirs.testruns / 'current_opendream.pickle', 'wb' ) as f:
        f.write( pickle.dumps(results) ) 
        
    with open(root_env.attr.dirs.storage / 'metadata' / 'test_runs.json', "w") as f:
        f.write( json.dumps( ["current_byond", "current_opendream"] ) )
    with open(root_env.attr.dirs.storage / 'metadata' / 'compares.json', "w") as f:
        f.write( json.dumps( [ ("current_byond", "current_opendream") ] ) )


asyncio.run( main() )