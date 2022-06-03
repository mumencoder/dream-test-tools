
from .common import *

class SS13App(object):
    async def update_ss13(self, env):
        env = self.env.branch()

        for repo_name, repo in env.attr.ss13.sources.items():
            env = self.env.branch()

            env.attr.git.repo.local_dir = env.attr.ss13.dirs.installs / repo_name
            env.attr.git.repo.url = repo["url"]
            if "branch" in repo:
                env.attr.git.repo.branch = repo["branch"]

            Shared.Workflow.set_task(env, Shared.Git.Repo.ensure(env) )

        await Shared.Workflow.run_all(self.env)

    async def parse_opendream_ss13(self, ssenv, open_id):
        try:
            await self.env.attr.resources.ss13.acquire(ssenv)
            await OpenDream.Compilation.compile(ssenv)
            self.load_ss13_test(ssenv)
            shutil.move( ssenv.attr.ss13.base_dir / "ast.json", ssenv.attr.test.base_dir / "ast.json")
        finally:
            self.env.attr.resources.ss13.release(ssenv)

    async def parse_clopendream_ss13(self, env):
        for ssenv in self.iter_ss13_tests(clenv):
            ssenv.attr.byond.compilation.file_path = ssenv.attr.ss13.dme_file

            Shared.Workflow.set_task(ssenv, self.parse_clopendream_ss13(ssenv, 'currentdev') )

        await Shared.Workflow.run_all(self.env)

    async def parse_clopendream_ss13(self, ssenv, clopen_id):
        try:
            await self.env.attr.resources.ss13.acquire(ssenv)

            btenv, ctenv = self.prepare_parse_clopendream_ss13(ssenv, clopen_id)

            await Byond.Compilation.generate_code_tree(btenv)

            await ClopenDream.Install.parse(ctenv)
        finally:
            self.env.attr.resources.ss13.release(ssenv)

    async def run_ss13_tests(self):
        async def run_opendream(self, ssenv):
            ssenv.attr.git.repo.local_dir = ssenv.attr.ss13.base_dir
            await Shared.Git.Repo.command(ssenv, 'git clean -fdx')

            ssenv.attr.opendream.compilation.dm_file = ssenv.attr.ss13.dme_file
            await self.parse_opendream_ss13(ssenv, 'ClopenDream-compat')

        for ssenv in self.iter_ss13_tests(oenv):
            Shared.Workflow.set_task(ssenv, self.run_opendream(ssenv) )

        await Shared.Workflow.run_all(self.env)

    async def compare_clopen_ss13(self):
        for ssenv in self.iter_ss13_tests(self.env):
            clenv = ssenv.branch()
            ClopenDream.Source.load(clenv, 'currentdev')
            ClopenDream.Install.load(clenv, 'currentdev')
            self.load_ss13_test(clenv)

            clenv.attr.clopendream.run.working_dir = clenv.attr.test.base_dir
            clod_json_path = clenv.attr.test.base_dir / 'clopen_ast.json'
            if not os.path.exists(clod_json_path):
                continue
            clenv.attr.clopendream.run.ast1 = clod_json_path

            oenv = ssenv.branch()
            OpenDream.Source.load(oenv, 'ClopenDream-compat')
            OpenDream.Install.load(oenv, 'ClopenDream-compat')
            self.load_ss13_test(oenv)
            od_json_path = oenv.attr.test.base_dir / 'ast.json'
            if not os.path.exists(od_json_path):
                continue
            clenv.attr.clopendream.run.ast2 = od_json_path

            Shared.Workflow.set_task(clenv, ClopenDream.Install.compare(clenv) )

            await Shared.Workflow.run_all(self.env)

    def prepare_parse_clopendream_ss13(self, ssenv, clopen_id):
        btenv = ssenv.branch()
        Byond.Install.load(btenv, 'main')
        self.load_ss13_test(btenv)
        btenv.attr.byond.compilation.out = btenv.attr.test.base_dir / 'ss13.codetree'

        ctenv = ssenv.branch()
        ClopenDream.Install.load(ctenv, clopen_id)
        self.load_ss13_test(ctenv)
        ctenv.attr.clopendream.install.working_dir = ctenv.attr.test.base_dir
        ctenv.attr.byond.codetree = btenv.attr.byond.compilation.out
        yield btenv, ctenv

    def load_ss13_test(self, env):
        env.attr.test.root_dir = env.attr.tests.dirs.output / f'ss13.{env.attr.ss13.repo_name}'
        env.attr.test.base_dir = env.attr.test.root_dir / f'{env.attr.install.platform}.{env.attr.install.id}'

    def iter_ss13_tests(self, env):
        for repo_name, repo in env.attr.ss13.sources.items():
            ssenv = env.branch()

            ssenv.attr.ss13.repo_name = repo_name
            ssenv.attr.ss13.base_dir = env.attr.ss13.dirs.installs / repo_name
            SS13.Install.find_dme( ssenv )
            if ssenv.attr.ss13.dme_file is None:
                continue

            yield ssenv