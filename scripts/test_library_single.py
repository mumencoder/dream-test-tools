
import asyncio
import Byond, OpenDream, ClopenDream

from DTT import App
import test_runner

class Main(App):
    async def run(self, test_file):
        Byond.Install.set_current(self.config, self.config['byond.version'])
        OpenDream.Install.set_current(self.config, self.config['opendream.build.id'])
        ClopenDream.Install.set_current(self.config, self.config['clopendream.build.id'])

        await test_runner.run_test(self.config, test_file, self.test_output_dir)

main = Main()
asyncio.run( main.run(main.config['tests_dir'] / 'dm' / 'testing.dm') )