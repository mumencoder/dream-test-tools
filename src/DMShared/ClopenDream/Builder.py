
from ..common import *

class Builder(object):
    @staticmethod
    def prepare_solution(env):
        env.attr.dotnet.project.path = env.attr.dotnet.solution.path

    @staticmethod
    async def build(env):
        renv = env.branch()
        Builder.prepare_solution(renv)
        await Shared.Dotnet.Project.restore( renv )

        benv = env.branch()
        if benv.has_attr('.clopendream.build.params'):
            benv.attr.dotnet.build.params = Shared.Dotnet.Project.default_params(benv.attr.clopendream.build.params)
        else:
            benv.attr.dotnet.build.params = {}

        if 'configuration' not in benv.attr.dotnet.build.params:
            benv.attr.dotnet.build.params['configuration'] = "Debug"

        Builder.prepare_solution(benv)
        await Shared.Dotnet.Project.build( benv )