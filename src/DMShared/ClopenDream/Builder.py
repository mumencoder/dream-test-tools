
from ..common import *

class Builder(object):
    @staticmethod
    def prepare_solution(env):
        env.attr.dotnet.project.path = env.attr.dotnet.solution.path

    @staticmethod
    async def build(env):
        build = env.prefix('.clopendream.build')
        dotnet = env.prefix('.dotnet')

        if env.has_attr('.clopendream.build.params'):
            dotnet.build.params = Shared.Dotnet.Project.default_params(build.params)
        else:
            dotnet.build.params = {}

        dotnet.build.params['configuration'] = 'Debug'

        env.attr.dotnet.solution.path = env.attr.install.dir
        cenv = env.branch()
        Builder.prepare_solution( cenv )

        crenv = cenv.branch()
        await Shared.Dotnet.Project.restore( crenv )

        cbenv = cenv.branch()
        if build.mode == "publish":
            await Shared.Dotnet.Project.publish( cbenv )
        else:
            await Shared.Dotnet.Project.build( cbenv )

        env.attr.restore_env = crenv
        env.attr.build_env = cbenv

    @staticmethod
    async def managed_build(env, build_metadata):
        env = env.branch()
        await Builder.build(env)
        if env.attr.restore_env.attr.process.instance.returncode != 0:
            raise Exception("restore failed")
        if env.attr.build_env.attr.process.instance.returncode != 0:
            raise Exception("build failed")
        status = await Shared.Git.Repo.status(env)
        build_metadata['last_build_commit'] = status['branch.oid']
