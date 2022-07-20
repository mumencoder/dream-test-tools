
from .common import *

from .Tests import *
from .Git import *
from .Compare import *
from .TestCase import *

class OpenDream(object):
    ############### Begin tasks ##############
    def load_build_from_commit(env, commit):
        env.attr.workflow.open( {'commit':commit} )
        OpenDream.build_from_github(env),
        OpenDream.load_build(env) 

    def build_opendream(env):
        if env.attr.opendream.last_build is not None:
            return
        if not env.attr.opendream.submodules_ready:
            Git.reset_submodule(env)
        await base.OpenDream.Builder.build(senv)
        if not base.OpenDream.Builder.build_ready(senv):
            return
        await env.send_event("opendream.build_ready", senv)

    class Providers(object):
        def 
    class OpenDreamProviders(object):
        def provide_github_repo_dir(env):
            return env.attr.opendream.dirs.repos / f'github.{env.attr.github.repo_id}.{env.attr.github.tag}'

    class OpenDreamBuildable(object):
        def provide_repo_dir(env):
            senv.attr.git.repo.local_dir = senv.attr.build.dir

    ####### loading tasks ######
    def build_from_github(env):
        env.attr.build.id = f"github.{env.attr.github.owner}.{env.attr.github.repo}.{env.attr.git.commit}.{env.attr.github.tag}"
        env.attr.build.dir = env.attr.opendream.dirs.installs / env.attr.build.id

    def build_from_local(env):
        env.attr.build.id = f"local.{env.attr.local.id}"
        env.attr.build.dir = env.attr.opendream.dirs.installs / env.attr.build.id
        await Shared.Path.full_sync_folders( env, env.attr.local.dir, env.attr.build.dir )

    def load_build(env):
        env.attr.install.platform = 'opendream'
        env.attr.platform_cls = base.OpenDream
        env.attr.dotnet.solution.path = senv.attr.build.dir
        env.attr.resources.compile = Shared.CountedResource(8)
        env.attr.resources.run = Shared.CountedResource(8)

    def load_worktree(env):
        env.attr.git.branch = env.attr.git.commit
        env.attr.git.worktree.commit = env.attr.git.commit
        env.attr.git.worktree.path = env.attr.build.dir

    def set_preproc_flags(env):
        if senv.attr.pr.info['id'] == 748018792:
            env.attr.compilation.args = {'flags':['experimental-preproc']}

    def run_tests(env):
        if len(senv.attr.tests.incomplete) == 0:
            return
        Tests.load_tests(env, 'default'),
        Tests.run_tests(env),
        Tests.save_complete_tests( env ),
        OpenDream.delete_build(env)

    def delete_build(env):
        if os.path.exists(env.attr.build.dir):
            shutil.rmtree(env.attr.build.dir)
