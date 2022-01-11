
import asyncio
import Byond, OpenDream, ClopenDream

from DTT import App
import test_runner

class Main(App):
    async def run(self, test_dir):
        Byond.Install.set_current(self.config, self.config['byond.version'])
        OpenDream.Install.set_current(self.config, self.config['opendream.build.id'])
        ClopenDream.Install.set_current(self.config, self.config['clopendream.build.id'])

        for test_file_path in test_runner.list_all_tests(self.config, test_dir):
            config = self.config.branch("test")
            await test_runner.read_single_test(self.config, self.config['tests_dir'], test_file_path, self.test_output_dir)
            await test_runner.test_all_platforms(self.config)

main = Main()
asyncio.run( main.run(main.config['tests_dir'] / 'dm') )