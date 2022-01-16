
import asyncio, time, os
import Byond, OpenDream, ClopenDream

from DTT import App
import test_runner

class Main(App):
    async def run(self, test_dir):
        installs = [ 
            {'platform':'byond','install_id':'default'}, 
            {'platform':'opendream','install_id':'default'},
            {'platform':'clopendream','install_id':'default', 'byond_install_id':'default'} 
        ]

        start_time = time.time()
        pending_tasks = []
        for test_file_path in test_runner.list_all_tests(self.config, test_dir):
            print(test_file_path)
            config = self.config.branch("test")
            for install in installs:
                config['test.platform'] = install['platform']
                config['test.install_id'] = install['install_id']
                test_runner.read_single_test(config, config['tests_dir'], test_file_path, self.test_output_dir)
                pending_tasks.append( asyncio.create_task( test_runner.test_install(config.copy(), install) ) )
                if len(pending_tasks) > 16:
                    await asyncio.gather( *pending_tasks )
                    pending_tasks = []
        await asyncio.gather( *pending_tasks )
        print(f"{time.time()-start_time}")
        os.system('stty sane')

main = Main()
asyncio.run( main.run(main.config['tests_dir'] / 'dm') )