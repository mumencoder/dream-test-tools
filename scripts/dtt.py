
import asyncio, time, os, sys, shutil
import collections

import Shared
import DTT
from DTT.base import *

class Main(DTT.App):
    def reset_dotnet(self):
        pses = Shared.Psutil.find(name='dotnet')
        for ps in pses:
            ps.kill()

    async def register_metrics(self, env):
        env.attr.test_counter = 0
        async def count_test():
            env.attr.test_counter += 1
        self.env.event_handlers["test.complete"] = count_test

        async def report_counter(penv, senv):
            start_time = time.time()
            while env.attr.scheduler.running:
                penv.attr.self_task.log( env.attr.test_counter / (time.time() - start_time) )
                await asyncio.sleep(30.0)

        Shared.Task.link( env.attr.scheduler.top_task, Shared.Task(env, report_counter, ptags={'action':'report_counter'}, background=True))

    async def add_byond_tests(self):
        env = self.env.branch()

        tasks = []
        tasks.append( DTT.tasks.Byond.load_install(env, self.env.attr.compares.ref_version ) )
        tasks.append( DTT.tasks.Byond.download(env).run_once() )
        tasks.append( DTT.tasks.Tests.load_tests(env, 'default') )
        subtasks = lambda env, tenv: Shared.Task.bounded_tasks(
            DTT.tasks.Tests.tag_test( env, tenv ), 
            DTT.tasks.Tests.check_test_runnable(env),
            DTT.tasks.Tests.do_test(env)
        )
        tasks.append( Shared.Task.subtask_source(env.branch(), '.tests.all_tests', subtasks, limit=32 ) )
        Shared.Task.chain( env.attr.scheduler.top_task, *tasks )

    async def prep_opendream(self):
        env = self.env.branch()

        self.processed_commits = Shared.AtomicSet()
        self.commits = {}
        self.installs = {}

        tasks = []
        tasks.append( Shared.Task.group(env, 'prep_opendream') )
        tasks.append( DTT.tasks.Git.initialize_github(env, 'wixoaGit', 'OpenDream', 'base') )
        self.tasks["wixoaGit.init_github"] = tasks[-1]
        tasks.append( DTT.tasks.OpenDream.source_from_github(env) )
        tasks.append( DTT.tasks.Git.freshen_repo(env).run_fresh(minutes=30) )
        tasks.append( DTT.tasks.Git.ensure_repo(env) )
        self.tasks["wixoaGit.ensure_repo"] = tasks[-1]
        tasks.append( DTT.tasks.OpenDream.create_shared_repos(env) )
        self.tasks["wixoaGit.shared_repos"] = tasks[-1]
        Shared.Task.chain( env.attr.scheduler.top_task, *tasks)

    async def prep_opendream_github(self):
        env = self.env.branch()
        self.tasks['wixoaGit.compare_init'] = DTT.tasks.OpenDream.initialize_github_compares(env)
        Shared.Task.link( env.attr.scheduler.top_task, self.tasks['wixoaGit.compare_init'] )
        Shared.Task.link( self.tasks["wixoaGit.init_github"], self.tasks['wixoaGit.compare_init'], ltype=["tag", "import"] )
    
    async def finish_opendream_github(self):
        env = self.env.branch()
        task = DTT.tasks.OpenDream.write_report(env)
        Shared.Task.link( self.tasks['wixoaGit.compare_init'], task)
        Shared.Task.link( self.tasks['wixoaGit.pr.finish'], task, ltype="exec" )
        Shared.Task.link( self.tasks['wixoaGit.history.finish'], task, ltype="exec" )

    def commit_tasks(self, env):
        return Shared.Task.bounded_tasks( 
            DTT.tasks.OpenDream.acquire_shared_repo( env ),
            DTT.tasks.Tests.load_tests(env, 'default'),
            DTT.tasks.OpenDream.process_commit(env), 
            DTT.tasks.OpenDream.release_shared_repo( env ),
            DTT.tasks.Tests.run_tests(env),
            DTT.tasks.Tests.save_complete_tests( env )
        )

    async def update_pull_requests(self):
        env = self.env.branch()

        tasks = [ ]
        tasks.append( Shared.Task.group(env, 'update_pull_requests') )
        tasks.append( DTT.tasks.Git.update_pull_requests(env) )
        tasks.append( Shared.Task.set_senv(env, '.opendream.processed_commits', self.processed_commits) )
        tasks.append( Shared.Task.set_senv(env, '.opendream.commits', self.commits ) )
        tasks.append( Shared.Task.set_senv(env, '.opendream.installs', self.installs ) )

        subtasks = lambda env, pull_info: Shared.Task.bounded_tasks(
            DTT.tasks.Git.tag_pull_request( env, pull_info ),
            DTT.tasks.OpenDream.acquire_shared_repo( env ),
            DTT.tasks.Git.load_pull_request( env ),
            DTT.tasks.OpenDream.release_shared_repo( env ),
            DTT.tasks.OpenDream.process_pr_commits( env, lambda: self.commit_tasks(env) ),
            DTT.tasks.OpenDream.load_pr_compare( env )
        )
        tasks.append( Shared.Task.subtask_source(env.branch(), '.prs.infos', subtasks, limit=4, tags={'action':'pr_subtasks'}) )
        tasks.append( DTT.tasks.OpenDream.pr_compare_report( env ) )
        self.tasks['wixoaGit.pr.finish'] = tasks[-1]

        Shared.Task.chain( env.attr.scheduler.top_task, *tasks )
        Shared.Task.link( self.tasks["wixoaGit.init_github"], tasks[0], ltype=["tag", "import"] )
        Shared.Task.link( self.tasks["wixoaGit.shared_repos"], tasks[0], ltype="import" )
        Shared.Task.link( self.tasks['wixoaGit.compare_init'], tasks[0], ltype="import" )

    async def update_commit_history(self, n):
        env = self.env.branch()

        tasks = [ ]
        tasks.append( Shared.Task.group(env, 'update_commit_history') )
        tasks.append( DTT.tasks.Git.update_commit_history(env, n) )
        tasks.append( Shared.Task.set_senv(env, '.opendream.processed_commits', self.processed_commits) )
        tasks.append( Shared.Task.set_senv(env, '.opendream.commits', self.commits ) ) 
        tasks.append( Shared.Task.set_senv(env, '.opendream.installs', self.installs ) )

        subtasks = lambda env, history_info: Shared.Task.bounded_tasks(
            DTT.tasks.Git.tag_history( env, history_info ),
            DTT.tasks.OpenDream.acquire_shared_repo( env ),
            DTT.tasks.Git.load_history( env ),
            DTT.tasks.OpenDream.release_shared_repo( env ),
            DTT.tasks.OpenDream.process_history_commit( env, lambda: self.commit_tasks(env) ),
        )
        tasks.append( Shared.Task.subtask_source(env.branch(), '.history.infos', subtasks, limit=4, tags={'action':'history_subtasks'}) )
        tasks.append( DTT.tasks.OpenDream.load_history_compares( env ) )
        tasks.append( DTT.tasks.OpenDream.history_compare_report( env ) )
        self.tasks['wixoaGit.history.finish'] = tasks[-1]

        Shared.Task.chain( env.attr.scheduler.top_task, *tasks )
        Shared.Task.link( self.tasks["wixoaGit.init_github"], tasks[0], ltype=["tag", "import"] )
        Shared.Task.link( self.tasks["wixoaGit.shared_repos"], tasks[0], ltype="import" )
        Shared.Task.link( self.tasks['wixoaGit.compare_init'], tasks[0], ltype="import" )

    ### local test
    def update_local(self, local_name, local_dir):
        env = self.env.branch()

        tasks = [  ]
        tasks.append( Shared.Task.group(env, 'update_local') )
        tasks.append( DTT.tasks.OpenDream.load_install_from_local(env, local_name, local_dir) )
        self.tasks["local.copy"] = tasks[-1]
        tasks.append( DTT.tasks.OpenDream.build_local(env) )
        tasks.append( DTT.tasks.Tests.clear_tests(env, 'default') )
        tasks.append( DTT.tasks.Tests.load_incomplete_tests(env, 'default') )
        tasks.append( DTT.tasks.Tests.run_incomplete_tests(env) )

        Shared.Task.chain( self.tasks["wixoaGit.init_github"], *tasks)

    async def test_base_commit(self):
        env = self.env.branch()
        env1 = self.tasks['wixoaGit.history_commits'].senv
        env2 = self.tasks["local.copy"].senv
        self.base_commit = Shared.Git.Repo.search_base_commit( env2, str(env2.attr.git.api.repo.head.commit), set(env1.attr.github.commit_history.keys()) )

        Shared.Workflow.init( self.env )
        Shared.Scheduler.init( self.env )

        tasks = []
        tasks.append( DTT.tasks.OpenDream.set_commit_tasks( env, [ DTT.tasks.OpenDream.load_install_from_github(env, self.base_commit) ] ) )
        tasks.append( DTT.tasks.OpenDream.process_commits(env) )
        Shared.Task.chain( self.env.attr.scheduler.top_task, *tasks)
        Shared.Task.link( self.tasks["wixoaGit.shared_repos"], tasks[0], ltype="import" )

        await Shared.Scheduler.run( self.env )

    async def compare_report_local(self):
        benv = self.env.branch()
        Byond.Install.load(benv, self.env.attr.compares.ref_version)

        cenv_base = self.tasks["wixoaGit.init_github"].senv.branch()
        cenv_base.attr.git.repo.commit = self.base_commit
        OpenDream.Install.from_github(cenv_base) 
        cenv_new = self.tasks["local.copy"].senv.branch()

        cenv = self.env.branch()
        cenv.attr.compare.ref = benv.branch()
        cenv.attr.compare.prev = cenv_base.branch()
        cenv.attr.compare.next = cenv_new.branch()
        compare_report = DTT.CompareReport(cenv)
        for tenv in DTT.TestCase.list_all(self.env.branch(), self.env.attr.tests.dirs.dm_files):
            DTT.TestCase.load_test_text(tenv)
            DTT.TestCase.wrap(tenv)
            ctenv = cenv.branch()
            ctenv.attr.compare.ref = benv.branch()
            ctenv.attr.compare.prev = cenv_base.branch()
            ctenv.attr.compare.next = cenv_new.branch()
            DTT.tasks.Compare.compare_test(ctenv, tenv)
            compare_report.add_compare_test( ctenv )

        DTT.BaseReport.write_report( self.env.attr.tests.dirs.reports / 'local', compare_report)

    ### master branch test
    async def test_main_branch(self):
        self.base_commit = self.tasks["wixoaGit.ensure_repo"].senv.attr.git.api.repo.remote('origin').refs["HEAD"].commit

        Shared.Workflow.init( self.env )
        Shared.Scheduler.init( self.env )

        env = self.env.branch()
        tasks = []
        tasks.append( DTT.tasks.Git.initialize_github(env, 'wixoaGit', 'OpenDream', 'master') )
        tasks.append( DTT.tasks.OpenDream.source_from_github(env) )
        tasks.append( DTT.tasks.Git.ensure_repo(env) )
        tasks.append( DTT.tasks.OpenDream.set_commit_tasks( env, [ DTT.tasks.OpenDream.load_install_from_github(env, self.base_commit) ] ) )
        tasks.append( DTT.tasks.OpenDream.process_commits(env) )
        Shared.Task.chain( self.env.attr.scheduler.top_task, *tasks )
        Shared.Task.link( self.tasks["wixoaGit.shared_repos"], tasks[0], ltype="import" )

    async def compare_report_main(self):
        benv = self.env.branch()
        Byond.Install.load(benv, self.env.attr.compares.ref_version)

        cenv_base = self.tasks["wixoaGit.init_github"].senv.branch()
        cenv_base.attr.git.repo.commit = self.base_commit
        OpenDream.Install.from_github(cenv_base) 

        cenv = self.env.branch()
        cenv.attr.compare.ref = benv.branch()
        cenv.attr.compare.prev = cenv_base.branch()
        cenv.attr.compare.next = None
        compare_report = DTT.CompareReport(cenv)
        for tenv in DTT.TestCase.list_all(self.env.branch(), self.env.attr.tests.dirs.dm_files):
            DTT.TestCase.load_test_text(tenv)
            DTT.TestCase.wrap(tenv)
            ctenv = cenv.branch()
            ctenv.attr.compare.ref = benv.branch()
            ctenv.attr.compare.prev = cenv_base.branch()
            ctenv.attr.compare.next = None
            DTT.tasks.Compare.compare_test(ctenv, tenv)
            compare_report.add_compare_test( ctenv )

        DTT.BaseReport.write_report( self.env.attr.tests.dirs.reports / 'main', compare_report)

    async def run_all(self):
        await self.run_byond()
        await self.run_opendream()
        await self.compare_reports()
        await Shared.Scheduler.run( self.env )

    async def full_history(self):
        history = 8
        while history < 256:
            Shared.Workflow.init( self.env )
            Shared.Scheduler.init( self.env )
            await self.init_top()
            await self.prep_opendream()
            await self.update_commit_history(history)
            await Shared.Scheduler.run( self.env )
            history += 8

    async def run_common(self):
        await self.init_top()
        await self.register_metrics(self.env)

    async def run_byond(self):
        await self.run_common()
        self.env.attr.compares.ref_version = '514.1566'
        await self.add_byond_tests()
        await Shared.Scheduler.run( self.env )

    async def run_opendream(self):
        await self.run_common()
        self.env.attr.compares.ref_version = '514.1566'
        await self.prep_opendream()
        await self.prep_opendream_github()
        await self.update_pull_requests()
        await self.update_commit_history(32)
        await self.finish_opendream_github()
        await Shared.Scheduler.run( self.env )

    async def run_local(self):
        await self.add_byond_tests()
        await self.prep_opendream()
        await self.update_commit_history(1)
        self.update_local('default', os.path.expanduser(self.cmd_args["dir"]) )
        await Shared.Scheduler.run( self.env )
        await self.test_base_commit()
        await Shared.Scheduler.run( self.env )
        await self.compare_report_local()

    async def run_main(self):
        await self.add_byond_tests()
        await self.prep_opendream()
        await Shared.Scheduler.run( self.env )
        await self.test_main_branch()
        await Shared.Scheduler.run( self.env )
        await self.compare_report_main()

    async def run(self):

        self.env.attr.config.redo_tests = []
        self.reset_dotnet()
        await self.run_tasks()

    def process_args(self):
        from optparse import OptionParser
        parser = OptionParser()
        self.cmd_args = {}
        if sys.argv[1] == "run_all":
            self.run_tasks = self.run_all
        elif sys.argv[1] == "run_byond":
            self.run_tasks = self.run_byond
        elif sys.argv[1] == "run_opendream":
            self.run_tasks = self.run_opendream
        elif sys.argv[1] == "run_local":
            self.run_tasks = self.run_local
            self.cmd_args["dir"] = sys.argv[2]
        elif sys.argv[1] == "run_main":
            self.run_tasks = self.run_main
        else:
            raise Exception("invalid command", sys.argv)
main = Main()
main.process_args()
asyncio.run( main.start() )