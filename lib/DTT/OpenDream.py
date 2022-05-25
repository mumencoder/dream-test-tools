
import os, asyncio

from .common import *

class OpenDreamApp(object):
    def task_initialize_from_github(self, env, source_suffix):
        github = env.prefix('.github')

        Shared.Task.tags(env, {'github.owner':github.owner, 'github.repo':github.repo, 'github.source_suffix':source_suffix} )
        env.attr.platform_cls = OpenDream

        async def load_source_task(penv, senv):
            senv.merge(penv, inplace=True)
            Shared.Github.prepare(senv)
            OpenDream.Source.from_github(senv, source_suffix)
            await Shared.Git.Repo.ensure(senv)

        t1 = Shared.Task(env, load_source_task, tags={'action':'load_source'})
        return t1

    def task_freshen_repo(self, env):
        async def freshen_task(penv, senv):
            await Shared.Git.Repo.freshen(senv)
            await Shared.Git.Repo.init_all_submodules(senv)
        t1 = Shared.Task(env, freshen_task, tags={'action':'freshen_task'}).run_fresh(minutes=30)
        return t1

    def task_create_shared_repos(self, env):
        async def copy_base_source(penv, senv):
            base_denv = penv.branch()
            senv.attr.resources.shared_opendream_repo = OpenDreamRepoResource(self.env, senv.attr.source.id, limit=4)
            for i in range(0, 4):
                denv = base_denv.branch()
                OpenDream.Source.load(denv, f'{senv.attr.source.id}.copy.{i}')
                await Shared.Path.full_sync_folders(senv, senv.attr.source.dir, denv.attr.source.dir)
        t1 = Shared.Task(env, copy_base_source, tags={'action':'copy_base_source'})
        return t1

    def tasks_update_pull_request(self, env):
        env = env.branch()

        async def refresh_pull_requests(penv, senv):
            penv.attr.scheduler.result_state.set(f'{senv.attr.github.repo_id}.prs', Shared.Github.list_pull_requests(senv) )
        t1 = Shared.Task(env, refresh_pull_requests, tags={'action':'refresh_pull_requests'}).run_fresh(minutes=30)

        async def process_pull_requests(penv, senv):
            prs = penv.attr.scheduler.result_state.get(f'{senv.attr.github.repo_id}.prs')
            build_commits = set()
            compare_commits = []

            try:
                while True:
                    repo = await senv.attr.resources.shared_opendream_repo.acquire()
                    if repo is not None:
                        break
                    await asyncio.sleep(0.2)
                renv = penv.branch()
                renv.attr.git.repo.local_dir = repo["data"]["path"]
                renv.attr.git.repo.remote = 'origin'
                await Shared.Git.Repo.ensure(renv)

                for pull_info in prs:
                    prenv = renv.branch()
                    prenv.attr.pull_info = pull_info

                    pr_commit = pull_info['merge_commit_sha']
                    prenv.attr.git.repo.remote_ref = pr_commit
                    await Shared.Git.Repo.ensure_commit(prenv)
                    if len(prenv.attr.git.api.repo.head.commit.parents) != 2:
                        raise Exception("expected 2 parent commits from PR sha", prenv.attr.git.api.repo.head.commit.parents)
                    for c in prenv.attr.git.api.repo.head.commit.parents:
                        if str(c) != pull_info["head"]["sha"]:
                            base_commit = str(c)

                    build_commits.add(base_commit)
                    build_commits.add(pr_commit)
                    compare_commits.append( {"pull_info":pull_info, "base":base_commit, "pr":pr_commit} )

            finally:
                senv.attr.resources.shared_opendream_repo.release(repo)

            penv.attr.scheduler.result_state.set(f'{senv.attr.github.repo_id}.prs.build_commits', list(build_commits) )
            penv.attr.scheduler.result_state.set(f'{senv.attr.github.repo_id}.prs.compare_commits', list(compare_commits) )
        t2 = Shared.Task(env, process_pull_requests, tags={'action':'process_pull_requests'}).run_fresh(minutes=30)

        async def schedule_pr_builds(penv, senv):
            commits = penv.attr.scheduler.result_state.get(f'{senv.attr.github.repo_id}.prs.build_commits' )
            for commit in commits:
                cenv = penv.branch()
                cenv.attr.build_commit = commit
                bt = Shared.Task(cenv, build_pull_request, tags={'commit':commit} ).run_once(final=process_build)
                tg.link( t3, bt )
        t3 = Shared.Task(env, schedule_pr_builds, tags={'action':'schedule_pr_builds'})

        async def build_pull_request(penv, senv):
            prenv = penv.branch()
            prenv.attr.github = senv.attr.github
            try:
                while True:
                    repo = await senv.attr.resources.shared_opendream_repo.acquire()
                    if repo is not None:
                        break
                    await asyncio.sleep(0.2)
                prenv.attr.git.repo.local_dir = repo["data"]["path"]
                prenv.attr.git.repo.remote = 'origin'
                await Shared.Git.Repo.ensure(prenv)
                OpenDream.Source.load( prenv, repo["data"]["source_id"] )

                prenv.attr.git.repo.remote_ref = penv.attr.build_commit
                await Shared.Git.Repo.ensure_commit(prenv)
                await Shared.Git.Repo.command(prenv, 'git clean -fdx')
                # deinit and reinit submodules here probably
                OpenDream.Install.from_github(prenv, 'defaults')
                await self.prepare_build(prenv)
                await OpenDream.Builder.build(prenv)

                penv.attr.final_state["install_id"] = prenv.attr.install.id
            finally:
                senv.attr.resources.shared_opendream_repo.release(repo)

        async def process_build(penv, senv):
            senv.attr.opendream_tests_queue.add( penv.attr.final_state['install_id'] ) 

        tg = Shared.TaskGraph( "update_pull_request", env, t1 )
        Shared.Task.chain(tg, t1, t2, t3)
        return tg

    async def compare_clopen_opendream(self, env):
        for tenv in test_runner.list_all_tests(self.env, self.env.attr.tests.dirs.dm_files):
            clenv = tenv.branch()
            ClopenDream.Source.load(clenv, 'currentdev')
            ClopenDream.Install.load(clenv, 'currentdev')

            test_runner.Curated.load_test( clenv )
            clenv.attr.clopendream.run.working_dir = clenv.attr.test.base_dir

            clod_json_path = clenv.attr.test.base_dir / 'clopen_ast.json'
            if not os.path.exists(clod_json_path):
                continue
            clenv.attr.clopendream.run.ast1 = clod_json_path

            oenv = tenv.branch()
            OpenDream.Source.load(oenv, 'ClopenDream-compat')
            OpenDream.Install.load(oenv, 'ClopenDream-compat')
            test_runner.Curated.load_test( oenv )

            od_json_path = oenv.attr.test.base_dir / 'ast.json'
            if not os.path.exists(od_json_path):
                continue
            clenv.attr.clopendream.run.ast2 = od_json_path

class OpenDreamRepoResource(Shared.ResourceTracker):
    def __init__(self, env, base_path, limit=None):
        self.env = env
        self.base_path = base_path
        super().__init__(limit=limit)

    def get_resource_data(self, i):
        data = {"id":i, "source_id": f'{self.base_path}.copy.{i}'}
        data["path"] = self.env.attr.opendream.dirs.sources / data["source_id"]
        return data

    def ensure_exist(self, data):
        data["path"].ensure_folder()