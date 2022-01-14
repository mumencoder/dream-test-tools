
import asyncio
import Byond, OpenDream, ClopenDream

from DTT import App
import test_runner

class Main(App):
    async def run(self, test_dir):
        installs = [ {'platform':'byond','install_id':'default'}, {'platform':'opendream','install_id':'default'} ]

        for test_file_path in test_runner.list_all_tests(self.config, test_dir):
            print(test_file_path)
            config = self.config.branch("test")
            await test_runner.read_single_test(config, config['tests_dir'], test_file_path, self.test_output_dir)
            for install in installs:
                await test_runner.test_install(config, install)

main = Main()
asyncio.run( main.run(main.config['tests_dir'] / 'dm') )