
import asyncio, time, os, sys, shutil
import collections

import Shared
import DTT
from DTT.base import *

class Main(DTT.App):
    async def add_byond_tests(self):
        self.byond_ref_version = '514.1566'

        env = self.env.branch()

        tasks = []
        tasks.append( DTT.tasks.Byond.load_install(env, self.byond_ref_version ) )
        tasks.append( DTT.tasks.Byond.download(env).run_once() )
        tasks.append( DTT.tasks.Tests.load_incomplete_tests(env, 'default') )
        tasks.append( DTT.tasks.Tests.run_incomplete_tests(env) )
        Shared.Task.chain( env.attr.scheduler.top_task, *tasks )

    async def prep_opendream(self):
        env = self.env.branch()
        Shared.Task.tags(env, {'task_group':'prep_opendream'})

        tasks = []
        tasks.append( DTT.tasks.Git.initialize_github(env, 'wixoaGit', 'OpenDream', 'base') )
        self.tasks["wixoaGit.init_github"] = tasks[-1]
        tasks.append( DTT.tasks.OpenDream.source_from_github(env) )
        tasks.append( DTT.tasks.Git.freshen_repo(env) )
        tasks.append( DTT.tasks.OpenDream.create_shared_repos(env) )
        self.tasks["wixoaGit.shared_repos"] = tasks[-1]
        Shared.Task.chain( env.attr.scheduler.top_task, *tasks)

    async def update_pull_requests(self):
        env = self.env.branch()
        Shared.Task.tags(env, {'task_group':'update_pull_requests'})

        tasks = []
        tasks.append( DTT.tasks.Git.initialize_github(env, 'wixoaGit', 'OpenDream', 'base') )
        tasks.append( DTT.tasks.Git.update_pull_requests(env) )
        tasks.append( DTT.tasks.OpenDream.load_pr_commits(env) )
        self.tasks['wixoaGit.prs'] = tasks[-1]
        tasks.append( DTT.tasks.OpenDream.process_commits(env) )
        Shared.Task.chain( env.attr.scheduler.top_task, *tasks )
        Shared.Task.link_exec( self.tasks["wixoaGit.shared_repos"], tasks[0] )

    async def update_commit_history(self):
        env = self.env.branch()
        Shared.Task.tags(env, {'task_group':'update_commit_history'})

        tasks = []
        tasks.append( DTT.tasks.Git.initialize_github(env, 'wixoaGit', 'OpenDream', 'base') )
        tasks.append( DTT.tasks.Git.update_commit_history(env) )
        tasks.append( DTT.tasks.OpenDream.load_history_commits(env, 16) )
        self.tasks[ 'wixoaGit.history_commits'] = tasks[-1]
        tasks.append( DTT.tasks.OpenDream.process_commits(env) )
        Shared.Task.chain( env.attr.scheduler.top_task, *tasks )
        Shared.Task.link_exec( self.tasks["wixoaGit.shared_repos"], tasks[0] )

    async def compare_reports(self):
        wixenv = self.tasks["wixoaGit.init_github"].senv

        self.root_report = DTT.RootReport("github")
        repo_report = DTT.GithubRepoReport(wixenv)
        self.root_report.add_report( repo_report )

        benv = self.env.branch()
        Byond.Install.load(benv, self.byond_ref_version)

        ghenv = self.tasks['wixoaGit.prs'].senv
        compares = ghenv.attr.opendream.compares
        for compare in compares:
            compare['cenv_ref'] = benv.branch()
            pr_report = DTT.PullRequestReport( repo_report, compare )
            repo_report.add_pr( pr_report )
            pr_report.compare_report = DTT.CompareReport(compare)
        for tenv in DTT.TestCase.list_all(self.env.branch(), self.env.attr.tests.dirs.dm_files):
            DTT.TestCase.load_test_text(tenv)
            DTT.TestCase.wrap(tenv)
            for compare in compares:
                cenv = self.env.branch()
                cenv.attr.compare.ref = compare['cenv_ref'].branch()
                cenv.attr.compare.prev = compare['cenv_base'].branch()
                cenv.attr.compare.next = compare['cenv_new'].branch()
                DTT.tasks.Compare.compare_test(cenv, tenv)
                repo_report.get_pr(compare['pull_info']["id"]).compare_report.add_test( cenv )

        ghenv = self.tasks['wixoaGit.history_commits'].senv
        compares = ghenv.attr.opendream.compares
        for compare in compares:
            compare['cenv_ref'] = benv.branch()
            history_report = DTT.CommitHistoryReport( repo_report, compare )
            repo_report.add_history( history_report )
            history_report.compare_report = DTT.CompareReport(compare)
        for tenv in DTT.TestCase.list_all(self.env.branch(), self.env.attr.tests.dirs.dm_files):
            DTT.TestCase.load_test_text(tenv)
            DTT.TestCase.wrap(tenv)
            for compare in compares:
                cenv = self.env.branch()
                cenv.attr.compare.ref = compare['cenv_ref'].branch()
                cenv.attr.compare.prev = compare['cenv_base'].branch()
                cenv.attr.compare.next = compare['cenv_new'].branch()
                DTT.tasks.Compare.compare_test(cenv, tenv)
                repo_report.get_history(compare['commit_info']['sha']).compare_report.add_test( cenv )

        self.write_report(self.root_report)

    async def run_tasks(self):
        await self.init_top()
        await self.add_byond_tests()
        await self.prep_opendream()
        await self.update_pull_requests()
        await self.update_commit_history()
        await Shared.Scheduler.run( self.env )

    async def run(self):
        await self.run_tasks()
        await self.compare_reports()


main = Main()
asyncio.run( main.start() )