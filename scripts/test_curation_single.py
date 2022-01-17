
import asyncio
import Byond, OpenDream, ClopenDream

from DTT import App
import test_runner

class Main(App):
    async def run(self, test_file):
        installs = [ {'platform':'byond','install_id':'default'}, {'platform':'opendream','install_id':'default'} ]
        config = self.config
        config['test.source_file'] = test_file 
        test_runner.get_test_info(config)
        test_runner.copy_test(config)
        for install in installs:
            await test_runner.test_install(self.config, install)

main = Main()
asyncio.run( main.run(main.config['tests.dirs.input'] / 'dm' / 'testing.dm') )