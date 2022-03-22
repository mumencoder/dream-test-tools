
import collections
import asyncio, time, os, sys
import Byond, OpenDream, ClopenDream, Shared

from DTT import App
import test_runner

class Main(App):
    async def run(self):
        env = self.env.branch()

        results = collections.defaultdict(list)
        mm_results = set()

        for tenv in test_runner.list_all_tests(env, main.env.attr.tests.dirs.dm_files):
            benv = tenv.branch()
            test_runner.Curated.load_test( benv )
            exists = test_runner.Report.load_result( benv )
            if not exists:
                continue
            
            oenv = tenv.branch()
            oenv.attr.opendream.sources['default_full'] = env.attr.opendream.sources['default']
            test_runner.Curated.load_test( oenv )
            exists = test_runner.Report.load_result( oenv )
            if not exists:
                continue

            if test_runner.Report.match_ccode( benv, oenv ) is False:
                mm_results.add( benv.attr.test.id )

            for pr in env.attr.state['github_prs']['data']:
                repo_name = pr["head"]["repo"]["full_name"].replace("/", ".")
                pr_sha = pr["head"]["sha"]
                install_id = f'github.{repo_name}.{pr_sha}'

                penv = tenv.branch()
                test_runner.Curated.load_test( penv )

                if not os.path.exists(penv.attr.test.base_dir / "compile.returncode.log"):
                    continue
                exists = test_runner.Report.load_result( penv )
                if not exists:
                    continue
                result = test_runner.Report.compare_results(benv, oenv, penv)

                if result in ["breaking", "fixing"]:
                    results[pr["title"]].append( (penv.attr.test.id, result) )

        print("=== PR Changes ===")
        for title, result in results.items():
            print(title)
            print(result)

        print("=== Mismatch ===")
        print(mm_results)

main = Main()
asyncio.run( main.start() )