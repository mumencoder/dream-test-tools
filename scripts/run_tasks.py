
import asyncio, time, os, sys
import collections

import Shared
import DTT
from DTT.base import *

class Main(DTT.App):
    async def init_top(self):
        self.tasks = {}
        self.env.attr.tasks.all_names = {}
        self.env.attr.tasks.base_tags = {}

        env = self.env.branch()

        self.top_task = Shared.Task.task_group(env, 'top')
        self.env.attr.tasks.top_task = self.top_task
        self.top_task.initialize(env)

        report_task = self.task_workflow_report()
        report_task.initialize(env)
        Shared.Scheduler.schedule( self.env, report_task )
        Shared.Scheduler.schedule( self.env, self.top_task )

    async def add_byond_tests(self):
        self.byond_ref_version = '514.1566'

        env = self.env.branch()

        tasks = []
        tasks.append( DTT.tasks.Byond.load_install(env, self.byond_ref_version ) )
        tasks.append( DTT.tasks.Byond.download(env).run_once() )
        tasks.append( DTT.tasks.Tests.load_incomplete_tests(env, 'default') )
        tasks.append( DTT.tasks.Tests.run_incomplete_tests(env) )
        Shared.Task.chain( self.top_task, *tasks )

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
        Shared.Task.chain( self.top_task, *tasks)

    async def update_pull_requests(self):
        env = self.env.branch()
        Shared.Task.tags(env, {'task_group':'update_pull_requests'})

        tasks = []
        tasks.append( DTT.tasks.Git.initialize_github(env, 'wixoaGit', 'OpenDream', 'base') )
        tasks.append( DTT.tasks.Git.update_pull_requests(env) )
        tasks.append( DTT.tasks.OpenDream.load_pr_commits(env) )
        tasks.append( DTT.tasks.OpenDream.process_commits(env) )
        Shared.Task.chain( self.top_task, *tasks )
        Shared.Task.link_exec( self.tasks["wixoaGit.shared_repos"], tasks[0] )

    async def update_commit_history(self):
        env = self.env.branch()
        Shared.Task.tags(env, {'task_group':'update_commit_history'})

        tasks = []
        tasks.append( DTT.tasks.Git.initialize_github(env, 'wixoaGit', 'OpenDream', 'base') )
        tasks.append( DTT.tasks.Git.update_commit_history(env) )
        tasks.append( DTT.tasks.OpenDream.load_history_commits(env, 32) )
        self.tasks[ 'wixoaGit.history_commits'] = tasks[-1]
        tasks.append( DTT.tasks.OpenDream.process_commits(env) )
        Shared.Task.chain( self.top_task, *tasks )
        Shared.Task.link_exec( self.tasks["wixoaGit.shared_repos"], tasks[0] )

    async def compare_reports(self):
        wixenv = self.tasks["wixoaGit.init_github"].senv

        self.setup_reports()
        repo_report = DTT.GithubRepoReport(wixenv)
        self.root_report.add_report( repo_report )

        pr_reports = {}
        compares = wixenv.attr.state.results.get(f'{wixenv.attr.github.repo_id}.prs.compare_commits')
        for compare in compares:
            pi = compare['pull_info']
            pr_report = DTT.PullRequestReport( repo_report, pi )
            pr_reports[pi["id"]] = pr_report

            compare["id"] = f'{self.byond_ref_version}.{compare["base"]}.{compare["pr"]}'
            compare["report"] = DTT.CompareReport(compare)
            repo_report.add_pr( pr_report )
            pr_report.compare_report = compare["report"]
        for tenv in DTT.TestCase.list_all(wixenv, self.env.attr.tests.dirs.dm_files):
            DTT.TestCase.load_test_text(tenv)
            for compare in compares:
                cenv = wixenv.branch()
                DTT.tasks.Compare.compare_load_environ(cenv, self.byond_ref_version, compare['base'], compare['pr'])
                cenv.merge(tenv, inplace=True)
                DTT.tasks.Compare.compare_test(cenv)
                pi = compare['pull_info']
                pr_report = pr_reports[pi["id"]]
                pr_report.compare_report.add_test( cenv )

        history_reports = {}
        compares = self.tasks['wixoaGit.history_commits'].senv.attr.opendream.history_compares
        for compare in compares:
            ci = compare['commit_info']
            history_report = DTT.CommitHistoryReport( repo_report, ci )
            history_reports[ci['sha']] = history_report

            compare["id"] = f'{self.byond_ref_version}.{compare["base"]}.{compare["new"]}'
            compare["report"] = DTT.CompareReport(compare)
            repo_report.add_history( history_report )
            history_report.compare_report = compare["report"]
        for tenv in DTT.TestCase.list_all(wixenv, self.env.attr.tests.dirs.dm_files):
            DTT.TestCase.load_test_text(tenv)
            for compare in compares:
                cenv = wixenv.branch()
                DTT.tasks.Compare.compare_load_environ(cenv, self.byond_ref_version, compare['base'], compare['new'])
                cenv.merge(tenv, inplace=True)
                DTT.tasks.Compare.compare_test(cenv)
                ci = compare['commit_info']
                history_report = history_reports[ci["sha"]]
                history_report.compare_report.add_test( cenv )

        self.write_reports()

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