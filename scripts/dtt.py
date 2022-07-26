
import asyncio, time, os, sys, shutil
import collections

import Shared
import DTT
from DTT.base import *

class Main(DTT.App):
    def run_common(self):
        self.env.attr.byond.install.version = '514.1566'
        self.init_top()
        self.env.attr.named_tasks = {}
        DTT.tasks.Monitoring.register_metrics(self.env)
        self.env.attr.cmd_args = self.cmd_args

    def run_byond(self, env):
        env = env.branch()
        tasks = [
            DTT.Byond.Setup.install(env),
            DTT.Byond.Setup.tests(env)
        ]
        return Shared.Task.bounded_tasks( *tasks )

    def run_opendream(self, env):
        env = env.branch()

        gh_task = DTT.tasks.OpenDream.Setup.github(env)

        pr_task = DTT.tasks.OpenDream.Setup.update_pull_requests(env)
        Shared.Task.link( gh_task, pr_task )

        ch_task = DTT.tasks.OpenDream.Setup.update_commit_history(env, n=env.attr.history.n)
        Shared.Task.link( gh_task, ch_task )
        Shared.Task.link( pr_task, ch_task, ltype="exec" )
      
        return Shared.TaskBound(gh_task, ch_task)

    def run_wix_main(self):
        env = self.env.branch()
        env.attr.history.n = 16
        async def set_github(penv, senv):
            senv.attr.github.owner = 'wixoaGit'
            senv.attr.github.repo = 'OpenDream'
            senv.attr.github.tag = ''
        Shared.Task.chain( env.attr.scheduler.top_task, self.run_byond(env) )
        Shared.Task.chain( env.attr.scheduler.top_task,
            Shared.Task(env, set_github, ptags={'action':'set_senv'}, unique=False),
            self.run_opendream(env)
        )

    def run_local(self):
        env = self.env.branch()
        
        def byond_install_load(senv):
            async def handler(ienv):
                env.attr.compare.ref = ienv
            senv.attr.test.cleared = True
            senv.event_handlers['install.load'] = handler

        byond_task = Shared.Task.bounded_tasks(
            Shared.Task.act_senv( env, byond_install_load ),
            self.run_byond(env)
        )
        Shared.Task.chain( env.attr.scheduler.top_task, byond_task )

        ### create github
        async def set_github(penv, senv):
            senv.attr.github.owner = 'wixoaGit'
            senv.attr.github.repo = 'OpenDream'
            senv.attr.github.tag = ''
        create_github = Shared.Task.bounded_tasks( 
            Shared.Task(env, set_github, ptags={'action':'set_senv'}, unique=False),
            DTT.tasks.OpenDream.Setup.github(env),
            Shared.Task.act_senv( env, Shared.Git.Repo.freshen ),
            DTT.tasks.Git.update_commit_history(env),
        )
        Shared.Task.link( env.attr.scheduler.top_task, create_github )

        ### create local
        async def set_local(penv, senv):
            senv.attr.local.id = self.cmd_args.id
            senv.attr.local.dir = Shared.Path( self.cmd_args.dir )
        async def get_head_commit(senv):
            senv.attr.git.commit = str(senv.attr.git.api.repo.head.commit)
        create_local = Shared.Task.bounded_tasks(
            Shared.Task(env, set_local, ptags={'action':'set_senv'}, unique=False),
            DTT.tasks.OpenDream.Setup.create_local(env),
            Shared.Task.act_senv( env, get_head_commit ),
        )
        Shared.Task.link( env.attr.scheduler.top_task, create_local )

        ### find base commit
        async def find_history_base_import(penv, senv):
            senv.attr.git.commit = penv.attr.self_task.links["local"].senv.attr.git.commit
            senv.attr.history.infos = penv.attr.self_task.links["github"].senv.attr.history.infos
        get_base = Shared.Task.bounded_tasks(
            Shared.Task.act( env, find_history_base_import ),
            DTT.tasks.Git.find_history_base_commit(env),
        )
        Shared.Task.link( create_local, get_base)
        Shared.Task.link( create_local, get_base, ltype="exec", name="local")
        Shared.Task.link( create_github, get_base, ltype="exec", name="github")

        ### update base
        def base_install_load(senv):
            async def handler(ienv):
                env.attr.compare.prev = ienv
            senv.attr.test.cleared = True
            senv.event_handlers['install.load'] = handler
        def import_commit(penv, senv):
            senv.attr.git.commits = [ penv.attr.self_task.links["base"].senv.attr.git.commit ]
        update_base = Shared.Task.bounded_tasks(
            Shared.Task.act_senv( env, base_install_load ),
            Shared.Task.act( env, import_commit ),
            DTT.tasks.OpenDream.Setup.update_commits(env)
        )
        Shared.Task.link( create_github, update_base)
        Shared.Task.link( get_base, update_base, ltype="exec", name="base")

        ### update local
        def merge_install_load(senv):
            async def handler(ienv):
                env.attr.compare.next = ienv
            senv.event_handlers['install.load'] = handler
            senv.attr.test.cleared = True
        update_local = Shared.Task.bounded_tasks(
            Shared.Task.act_senv( env, merge_install_load ),
            DTT.tasks.OpenDream.Setup.update_local(env)
        )
        Shared.Task.link( create_local, update_local )

        final_task = Shared.Task.bounded_tasks(
            Shared.Task.group(env, 'final_tasks'),
            Shared.Task.action( env, lambda: DTT.tasks.Compare.report(env), tags={'action':'report'})
        )
        Shared.Task.chain( env.attr.scheduler.top_task, final_task )
        Shared.Task.link(byond_task, final_task, ltype="exec")
        Shared.Task.link(update_base, final_task, ltype="exec")
        Shared.Task.link(update_local, final_task, ltype="exec")

    def clean_data(self):
        import shutil
        shutil.rmtree( self.env.attr.dirs.root )

    async def run(self):
        self.env.attr.config.redo_tests = []
        Shared.Dotnet.reset()
        self.run_common()
        self.run_tasks()
        await Shared.Scheduler.run( self.env )

    def process_args(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--experimental-preproc', action='store_true', dest="experimental_preproc")
        if sys.argv[1] == "":
            pass
        elif sys.argv[1] == "run_wix_main":
            self.run_tasks = self.run_wix_main
        elif sys.argv[1] == "run_local":
            parser.add_argument('id')
            parser.add_argument('dir')
            self.run_tasks = self.run_local
        elif sys.argv[1] == "clean_data":
            self.run_tasks = self.clean_data
        else:
            raise Exception("invalid command", sys.argv[1])
        self.cmd_args = parser.parse_args(args=sys.argv[2:])

main = Main()
main.process_args()
asyncio.run( main.start() )