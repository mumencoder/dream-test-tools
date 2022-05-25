
import asyncio, time, os, sys
import collections
import Byond, OpenDream, ClopenDream, Shared

import DTT

class Main(DTT.App):
    def task_group(self, group_name):
        async def pass_task(penv, senv):
            pass           
        return Shared.Task(self.env, pass_task, tags={'grouped_tasks':group_name} )

    async def run_init(self):
        self.env.attr.task_names = set()
        self.env.attr.deps_dag = Shared.DirectedGraph()
        await Shared.Scheduler.schedule( self.env, self.task_workflow_report() )

        wixenv = self.env.branch()
        wixenv.attr.github.owner = 'wixoaGit'
        wixenv.attr.github.repo = 'OpenDream'
        self.wixenv = wixenv

        self.top_group = self.task_group('top')

        top = Shared.TaskGraph( "top", self.env.branch(), self.top_group )
        self.top_graph = top

        opend_env = self.env.branch()
        self.opend_env = opend_env


    async def run_byond_tests(self):
        tenv = self.env.branch()
        tg = self.byond_tasks(tenv)
        tg.initialize(tenv)
        tg.start()
        await Shared.Scheduler.schedule( tenv, tg )
        await Shared.Scheduler.run( tenv )

    async def prep_opendream(self):
        wixenv = self.wixenv
        opend_env = self.opend_env
        top = self.top_graph

        opend_env.attr.opendream_tests_queue = set()
        opend_env.attr.opendream_compare_queue = []
        top.initialize(opend_env)

        t1 = self.task_initialize_from_github(wixenv, 'base')
        top.link( self.top_group, t1 )
        t2 = self.task_freshen_repo(wixenv)
        top.link( t1, t2 )
        t3 = self.task_create_shared_repos(wixenv)
        top.link( t2, t3 )
        t4 = self.tasks_update_pull_request(wixenv)
        top.link( t3, t4 )

        top.start()
        await Shared.Scheduler.schedule( opend_env, self.task_workflow_report() )
        await Shared.Scheduler.schedule( opend_env, top )
        await Shared.Scheduler.run( opend_env )

    async def run_opendream_tests(self):
        top = self.top_graph
        opend_env = self.opend_env
        for install_id in self.opend_env.attr.opendream_tests_queue:
            print(install_id)
            ienv = opend_env.branch()
            ienv.attr.platform_cls = OpenDream
            ienv.attr.resources.opendream_server = Shared.CountedResource(1)
            Shared.Task.tags(ienv, {'install':install_id})
            OpenDream.Install.load(ienv, install_id)
            for test_task in self.load_test_tasks(ienv):
                top.link( self.top_group, test_task )

        top.start()
        await Shared.Scheduler.run( opend_env )

        #await self.byond_stuff()
        #await self.main_opendream_stuff()

    async def compare_reports(self):
        wixenv = self.env.branch()
        wixenv.attr.github.owner = 'wixoaGit'
        wixenv.attr.github.repo = 'OpenDream'
        Shared.Github.prepare(wixenv)
        compares = wixenv.attr.scheduler.result_state.get(f'{wixenv.attr.github.repo_id}.prs.compare_commits')
        summary = {}
        for compare in compares:
            pi = compare['pull_info']
            n = pi["number"]
            summary[n] = {"title":pi['title'], "results":collections.defaultdict(int)}

        self.setup_reports()
        repo_report = DTT.GithubRepoReport(wixenv)

        self.root_report.add_report( repo_report )

        pr_reports = {}
        for compare in compares:
            pi = compare['pull_info']
            pr_reports[pi["id"]] = DTT.PullRequestReport( repo_report, pi )

            compare["id"] = f'{self.byond_ref_version}.{compare["base"]}.{compare["pr"]}'
            compare["report"] = DTT.CompareReport(compare)
            pr_report = pr_reports[pi["id"]]
            repo_report.add_pr( pr_report )
            pr_report.compare_report = compare["report"]

        for tenv in DTT.TestCase.list_all(wixenv, self.env.attr.tests.dirs.dm_files):
            DTT.TestCase.load_test_text(tenv)
            for compare in compares:
                cenv = wixenv.branch()
                self.compare_load_environ(cenv, self.byond_ref_version, compare['base'], compare['pr'])
                cenv.merge(tenv, inplace=True)
                self.compare_test(cenv)
                pi = compare['pull_info']
                summ = summary[pi['number']]
                summ['results'][ cenv.attr.compare.result ] += 1
                pr_report = pr_reports[pi["id"]]
                pr_report.compare_report.add_test( cenv )
        
        for summ in summary.values():
            print(summ['title'])
            print(summ['results'])

        self.write_reports()

    async def run(self):
        self.byond_ref_version = '514.1566'
        await self.run_init()
        #await self.run_byond_tests()
        await self.prep_opendream()
        #await self.run_opendream_tests()
        await self.compare_reports()
        await asyncio.sleep(5.0)


main = Main()
asyncio.run( main.start() )