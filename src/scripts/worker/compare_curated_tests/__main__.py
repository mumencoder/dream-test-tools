
from common import *

root_env = base_env()
load_config( root_env, sys.argv[1] )

byond_install_dir = root_env.attr.dirs.storage / 'byond_install'
opendream_install_dir = root_env.attr.dirs.storage  / 'opendream_install' / 'main'
tests_dir = root_env.attr.dirs.dtt / 'resources' / 'dm' / 'curated' 

async def install():
    pass

async def main():
    byond_version = list(sorted( os.listdir(byond_install_dir), reverse=True ))[0]

    benv = root_env.branch()
    benv.attr.install.dir = byond_install_dir / byond_version

    oenv = root_env.branch()
    oenv.attr.git.repo.url = 'https://github.com/OpenDreamProject/OpenDream'
    oenv.attr.git.repo.dir = opendream_install_dir

    oenv.attr.opendream.build_metadata = root_env.attr.dirs.storage / 'metadata' / 'opendream_install_main.pckl' 
    DMShared.OpenDream.Install.load_install_from_repo(oenv)
    oenv.attr.install.dir = opendream_install_dir

    def reset_test():
        if os.path.exists( r_tenv.attr.test.base_dir ):
            shutil.rmtree( r_tenv.attr.test.base_dir )
        DMShared.DMSource.TestCase.load_test(tenv)
        DMShared.DMSource.TestCase.write(tenv)

    r_tenv = root_env.branch()
    r_tenv.attr.test.base_dir = root_env.attr.dirs.tmp / 'tests' / 'current'
    r_tenv.attr.results = {}
    test_results = {}

    async def termination_check(env):
        if os.path.exists( os.path.join(env.attr.shell.dir, 'fin') ):
            return True
        elif Shared.Process.limited_process(env, time_limit=5.0, memory_limit=1*1024**3):
            return True
        return False
    
    benv.attr.process.try_terminate = termination_check
    oenv.attr.process.try_terminate = termination_check
    for tenv in DMShared.DMSource.TestCase.iter_tests( r_tenv, tests_dir ):
        start_time = time.time()
        print( tenv.attr.test.source_file )
        test_result = {}

        # Byond
        reset_test()
        test_result["byond"] = {}

        cenv = benv.branch()
        cenv.attr.compilation.root_dir = r_tenv.attr.test.base_dir
        cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
        await DMShared.Byond.Compilation.managed_compile(cenv)
        test_result["byond"]["compile.returncode"] = cenv.attr.compile.returncode
        test_result["byond"]["compile.stdout"] = cenv.attr.compile.stdout 

        if cenv.attr.compile.returncode == 0:
            renv = benv.branch()
            DMShared.Byond.Run.prepare_from_compilation(renv, cenv)
            await DMShared.Byond.Run.managed_run(renv)

            test_result["byond"]["run.returncode"] = renv.attr.run.returncode
            test_result["byond"]["run.stdout"] = renv.attr.run.stdout

            DMShared.DMSource.TestCase.load_result(tenv)
            test_result["byond"]["run.run_out"] = tenv.attr.result.run_out
            test_result["byond"]["run.run_unexpected_out"] = tenv.attr.result.run_unexpected_out

        # OpenDream
        reset_test()
        test_result["opendream"] = {}

        cenv = oenv.branch()
        cenv.attr.compilation.root_dir = r_tenv.attr.test.base_dir
        cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
        await DMShared.OpenDream.Compilation.managed_compile(cenv)
        test_result["opendream"]["compile.returncode"] = cenv.attr.compile.returncode
        test_result["opendream"]["compile.stdout"] = cenv.attr.compile.stdout 

        if cenv.attr.compile.returncode == 0:
            renv = oenv.branch()
            DMShared.OpenDream.Run.prepare_from_compilation(renv, cenv)
            await DMShared.OpenDream.Run.managed_run(renv)

            test_result["opendream"]["run.returncode"] = renv.attr.run.returncode
            test_result["opendream"]["run.stdout"] = renv.attr.run.stdout

            DMShared.DMSource.TestCase.load_result(tenv)
            test_result["opendream"]["run.run_out"] = tenv.attr.result.run_out
            test_result["opendream"]["run.run_unexpected_out"] = tenv.attr.result.run_unexpected_out

        test_results[tenv.attr.test.source_file] = test_result
        with open( root_env.attr.dirs.storage / 'monitor.pickle', 'wb' ) as f:
            f.write( pickle.dumps(test_results) ) 

        print( time.time() - start_time )

asyncio.run( main() )