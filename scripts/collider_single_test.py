
import asyncio
import Byond, OpenDream

from DTT import App
import test_runner

class Main(App):
    async def run(self, test):
        Byond.Install.set_current(self.config, self.config['byond.version'])
        self.config['test.platform'] = 'byond'
        config = await test_runner.test_prep.single_fixed_test(self.config, self.config['tests_dir'], test, self.test_output_dir)
        await test_runner.byond.compile(config)
        await test_runner.byond.run(config)

        OpenDream.Install.set_current(self.config, self.config['opendream.build.id'])
        self.config['test.platform'] = 'opendream'
        config = await test_runner.test_prep.single_fixed_test(self.config, self.config['tests_dir'], test, self.test_output_dir)
        await test_runner.opendream.compile(config)
        await test_runner.opendream.run(config)

main = Main()
asyncio.run( main.run(main.config['tests_dir'] / 'dm' / 'stdlib' / 'sound_flags.dm') )
