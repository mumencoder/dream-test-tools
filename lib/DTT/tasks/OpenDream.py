
from .common import *

from .Tests import *
from .Git import *
from .Compare import *
from .TestCase import *

class OpenDream(object):
    class Setup(object):
        def github(env):
            tasks = []
            tasks.append( Shared.Task.act_senv( env, Shared.Github.prepare ) )
            tasks.append( OpenDream.repo_from_github(env) )
            env.attr.named_tasks["OpenDream.github"] = tasks[-1]
            return Shared.Task.bounded_tasks( *tasks )
        
        def update_pull_requests(env):
            t1 = Shared.Task.bounded_tasks(
                Shared.Task.group(env, 'OpenDream.update_pull_requests'),
                Git.update_pull_requests(env),
                Git.gather_pr_commits(env),
                Shared.Task.assign_senv(env, dst='.git.commits', src=Git.unique_pr_commits),
            )
            t2 = OpenDream.create_worktrees(env)
            Shared.Task.link( t1, t2 )

            t3 = OpenDream.process_commits(env, 'process_pr_commits')
            Shared.Task.link( t1, t3 )
            Shared.Task.link( t2, t3, ltype='exec' )

            return Shared.TaskBound( t1, t3 )

        def update_commit_history(env, n=None):
            t1 = Shared.Task.bounded_tasks(
                Shared.Task.group(env, 'OpenDream.update_commit_history'),
                Git.update_commit_history(env),
                Git.gather_history_commits(env, n=n),
                Shared.Task.assign_senv(env, dst='.git.commits', src=Git.unique_history_commits),
            )
            t2 = OpenDream.create_worktrees(env)
            Shared.Task.link( t1, t2 )

            t3 = OpenDream.process_commits(env, 'process_history_commits')
            Shared.Task.link( t1, t3 )
            Shared.Task.link( t2, t3, ltype='exec' )

            return Shared.TaskBound( t1, t3 )

        def update_commits(env):
            t1 = Shared.Task.bounded_tasks(
                Shared.Task.group(env, 'OpenDream.update_commits'),
            )
            t2 = OpenDream.create_worktrees(env)
            Shared.Task.link( t1, t2 )

            t3 = OpenDream.process_commits(env, 'process_head_commits')
            Shared.Task.link( t1, t3 )
            Shared.Task.link( t2, t3, ltype='exec' )

            return Shared.TaskBound( t1, t3 )

        def create_local(env):
            return Shared.Task.bounded_tasks(
                Shared.Task.group(env, 'OpenDream.create_local'),
                OpenDream.build_from_local(env),
                OpenDream.repo_from_build(env),
                OpenDream.load_build(env)
            )

        def update_local(env):
            return Shared.Task.bounded_tasks(
                Shared.Task.group(env, 'OpenDream.update_local'),
                Git.reset_submodule(env),
                OpenDream.build_opendream( env ),
                Tests.clear_tests( env ),
                OpenDream.run_tests( env )
            )

    ############### Begin tasks ##############
    def load_build_from_commit(env, commit):
        return Shared.Task.bounded_tasks(
            Shared.Task.add_stags(env, {'commit':commit} ),
            Shared.Task.set_senv(env, '.git.commit', commit),
            OpenDream.build_from_github(env),
            OpenDream.load_build(env) 
        )

    def process_commits(env, group):
        def task_proto(penv, senv, commit):
            return Shared.Task.bounded_tasks(
                Shared.Task.add_stags(env, {'group2':group} ),
                OpenDream.load_build_from_commit(env, commit),
                OpenDream.repo_from_build(env),
                Shared.Task.act_senv( env, Shared.Git.Repo.init_all_submodules ),
                OpenDream.build_opendream( env ),
                OpenDream.run_tests( env )
            )
        return Shared.Task.subtask_source(env, '.git.commits', task_proto, limit=4)

    def create_worktrees(env):
        def task_proto(penv, senv, commit):
            return Shared.Task.bounded_tasks(
                Shared.Task.add_stags(env, {'group2':'create_worktrees'} ),
                OpenDream.load_build_from_commit(env, commit),
                OpenDream.load_worktree(env),
                Shared.Task.act_senv( env, Shared.Git.Repo.ensure_worktree )
            )
        return Shared.Task.serial_loop(env, '.git.commits', task_proto)

    def build_opendream(env):
        async def task(penv, senv):
            await base.OpenDream.Builder.build(senv)
            if not base.OpenDream.Builder.build_ready(senv):
                penv.attr.self_task.halt()
            await senv.send_event("install.load", senv)
        return Shared.Task(env, task, ptags={'action':'build_opendream'})

    ####### loading tasks ######
    def repo_from_github(env):
        async def task(penv, senv):
            senv.attr.git.repo.local_dir = senv.attr.opendream.dirs.repos / f'github.{senv.attr.github.repo_id}.{senv.attr.github.tag}'
            senv.attr.git.remote = 'origin'
            await Shared.Git.Repo.ensure(senv)
            Shared.Git.Repo.load(senv)
        return Shared.Task(env, task, ptags={'action':'repo_from_github'})

    def repo_from_build(env):
        async def task(penv, senv):
            senv.attr.git.repo.local_dir = senv.attr.build.dir
            Shared.Git.Repo.load(senv)
        return Shared.Task(env, task, ptags={'action':'repo_from_build'})

    def build_from_github(env):
        async def task(penv, senv):
            senv.attr.install.id = f"github.{senv.attr.github.owner}.{senv.attr.github.repo}.{senv.attr.git.commit}.{senv.attr.github.tag}"
            senv.attr.build.dir = senv.attr.opendream.dirs.installs / senv.attr.install.id
        return Shared.Task(env, task, ptags={'action':'build_from_github'})

    def build_from_local(env):
        async def task(penv, senv):
            senv.attr.install.id = f"local.{senv.attr.local.id}"
            senv.attr.build.dir = senv.attr.opendream.dirs.installs / senv.attr.install.id
            await Shared.Path.full_sync_folders( senv, senv.attr.local.dir, senv.attr.build.dir )
        return Shared.Task(env, task, ptags={'action':'build_from_local'})

    def load_build(env):
        async def task(penv, senv):
            senv.attr.install.platform = 'opendream'
            senv.attr.platform_cls = base.OpenDream
            senv.attr.dotnet.solution.path = senv.attr.build.dir
            OpenDream.config_build(senv)
        return Shared.Task(env, task, ptags={'action':'load_build'} )

    def config_build(env):
        env.attr.resources.compile = Shared.CountedResource(8)
        env.attr.resources.run = Shared.CountedResource(8)

    def load_worktree(env):
        async def task(penv, senv):
            senv.attr.git.branch = senv.attr.git.commit
            senv.attr.git.worktree.commit = senv.attr.git.commit
            senv.attr.git.worktree.path = senv.attr.build.dir
        return Shared.Task(env, task, ptags={'action':'create_worktree'})

    def set_preproc_flags(env):
        async def task(penv, senv):
            # TODO: better way to do this
            if senv.attr.pr.info['id'] == 748018792:
                extra_task = Shared.Task.set_senv(env, '.compilation.args', {'flags':['experimental-preproc']})
            else:
                extra_task = Shared.Task.nop(env)
        return Shared.Task(env, task, ptags={'action':'set_preproc_flags'} )

    def run_tests(env):
        return Shared.Task.bounded_tasks( 
            Tests.load_tests(env, 'default'),
            OpenDream.halt_if_no_incomplete_tests(env),
            Tests.run_tests(env),
            Tests.save_complete_tests( env )
        )

    def halt_if_no_incomplete_tests(env):
        async def task(penv, senv):
            if len(senv.attr.tests.incomplete) == 0:
                penv.attr.self_task.halt()
        return Shared.Task(env, task, ptags={'action':'process_commit'})

