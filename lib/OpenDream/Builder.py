
import asyncio

import os
import pathlib

import Shared

class Source(object):
    @staticmethod
    def load(env, _id):
        source = env.prefix('.opendream.source')
        source.id = _id
        source.info = env.attr.opendream.sources[_id]
        source.dir = env.attr.opendream.dirs.sources / source.id
        source.install_dir = env.attr.opendream.dirs.installs / source.id

    @staticmethod
    @Shared.wf_tag('source.ensure')
    async def ensure(env):
        source = env.prefix('.opendream.source')
        with Shared.Workflow.status(env, "fetch opendream source"):
            env.attr.dotnet.solution.path = source.dir
            if source.info["type"] == "filesystem":
                with Shared.Workflow.status(env, "sync folders"):
                    Shared.Path.sync_folders( source.info["location"], source.dir )
                env.attr.git.repo.local_dir = source.dir
                await Shared.Git.Repo.ensure(env)
            if source.info["type"] == "pr":
                with Shared.Workflow.status(env, "sync folders"):
                    Shared.Path.sync_folders( source.info["base_location"], source.dir )
                env.attr.git.repo.local_dir = source.dir
                await Shared.Git.Repo.ensure(env)
                repo = env.attr.git.api.repo
                pr = source.info["pr"]
                if 'pr' not in repo.remotes:
                    repo.create_remote('pr', url=pr["head"]["repo"]["clone_url"])
                if 'pr' not in repo.refs:
                    repo.remotes['pr'].fetch(f'{pr["head"]["ref"]}')
                repo.head.reset(repo.refs['master'], working_tree=True)
                repo.remotes['pr'].pull(f"{pr['head']['ref']}")
            if source.info["type"] == "repo":
                env.attr.git.repo.url = source.info["url"]
                env.attr.git.repo.local_dir = source.dir
                env.attr.git.repo.branch = source.info["branch"]
                await Shared.Git.Repo.ensure(env)
                await Shared.Git.Repo.init_all_submodules(env)

class Builder(object):
    @staticmethod
    def prepare_compiler_build(env):
        env.attr.dotnet.project.path = env.attr.dotnet.solution.path / "DMCompiler" / 'DMCompiler.csproj'

    @staticmethod
    def prepare_server_build(env):
        env.attr.dotnet.project.path = env.attr.dotnet.solution.path / 'OpenDreamServer' / 'OpenDreamServer.csproj'

    @staticmethod
    @Shared.wf_tag('opendream.build')
    async def build(env):
        source = env.prefix('.opendream.source')
        env.attr.dotnet.solution.path = source.dir

        if env.attr_exists('.opendream.build.params'):
            env.attr.dotnet.build.params = Shared.Dotnet.Project.default_params(env.attr.opendream.build.params)
        else:
            env.attr.dotnet.build.params = {}

        #env.attr.dotnet.build.params['output'] = source.install_dir

        env2 = env.branch()
        Builder.prepare_compiler_build( env2 )

        env3 = env2.branch()
        await Shared.Dotnet.Project.restore( env3 )
        env3 = env2.branch()
        await Shared.Dotnet.Project.build( env2 )

        env2 = env.branch()
        Builder.prepare_server_build( env2 )
        await Shared.Dotnet.Project.build( env2 )
