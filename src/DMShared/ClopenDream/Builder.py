
from ..common import *

class Builder(object):
    @staticmethod
    def prepare_solution(env):
        env.attr.dotnet.project.path = env.attr.dotnet.solution.path

    @staticmethod
    async def build(env):
        renv = env.branch()
        await Shared.Dotnet.Project.restore( renv )

        if env.attr_exists('.clopendream.build.params'):
            env.attr.dotnet.build.params = Shared.Dotnet.Project.default_params(env.attr.clopendream.build.params)
        else:
            env.attr.dotnet.build.params = {}

        if 'configuration' not in env.attr.dotnet.build.params:
            env.attr.dotnet.build.params['configuration'] = "Debug"

        benv = env.branch()
        Builder.prepare_solution(benv)
        await Shared.Dotnet.Project.build( benv )