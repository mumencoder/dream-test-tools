
import datetime as dt
import asyncio, time, os
import git

import collections

import Byond, OpenDream, ClopenDream, Shared
from DTT import App
import test_runner

class Main(App):
    async def run(self):
        oenv = self.env.branch()

        results = collections.defaultdict(list)

        oenv.attr.opendream.sources['default_full_history'] = oenv.attr.opendream.sources['default']
        oenv.attr.git.repo.clone_depth = 512
        OpenDream.Source.load(oenv, 'default_full_history')
        oenv.attr.opendream.install.dir = oenv.attr.opendream.source.dir

        repo = git.Repo( oenv.attr.opendream.source.dir )
        commit = repo.commit('origin/HEAD~0')
        print(commit)

        oenv.attr.git.repo = repo
        repo.remote('origin').pull(depth=512)

        commits = Shared.Git.Repo.commit_history(commit, depth=16)
        first_commit = None
        for second_commit in commits:
            if first_commit is None:
                first_commit = second_commit
                continue

            print("===", first_commit, second_commit)
            for tenv in test_runner.list_all_tests(self.env, main.env.attr.tests.dirs.dm_files):
                benv = tenv.branch()
                Byond.Install.load(benv, 'default')
                test_runner.Curated.load_test( benv )
                exists = test_runner.Report.load_result( benv )
                if not exists:
                    continue

                env1 = tenv.branch()
                Opendream.Source.load(env1, f'github.main.{str(first_commit)}')
                test_runner.Curated.load_test( env1 )
                exists = test_runner.Report.load_result( env1 )
                if not exists:
                    continue

                env2 = tenv.branch()
                Opendream.Source.load(env2, f'github.main.{str(second_commit)}')
                test_runner.Curated.load_test( env2 )
                test_runner.Curated.load_test( env2 )
                exists = test_runner.Report.load_result( env2 )
                if not exists:
                    continue

                result = test_runner.Report.compare_results(benv, env2, env1)

                result_id = f"{second_commit.summary} {second_commit} -> {first_commit.summary} {first_commit}"
                if result in ["breaking", "fixing"]:
                    results[result_id].append( (benv.attr.test.id, result) )

            first_commit = second_commit

        print("=== Changes ===")
        for title, result in results.items():
            print(title)
            print(result)

main = Main()
asyncio.run( main.start() )