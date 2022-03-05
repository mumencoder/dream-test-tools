

import datetime as dt
import asyncio, time, os
import git

import Byond, OpenDream, ClopenDream, Shared
from DTT import App
import test_runner

class Main(App):
    async def run(self, test_dir):

        OpenDream.Install.set_current(self.config, 'default')
        repo = git.Repo( self.config['opendream.install.dir'] )
        repo.remote('origin').pull(depth=512)

        commit = repo.commit('HEAD~0')
        self.config['git.repo'] = repo

        commits = Shared.Git.nightly_builds( Shared.Git.Repo.commit_history(self.config, commit, depth=256) )
        for c in commits:
            repo.head.reference = repo.head.reference = c
            repo.head.reset(index=True, working_tree=True)

main = Main()
asyncio.run( main.run(main.config['tests.dirs.input'] / 'dm') )