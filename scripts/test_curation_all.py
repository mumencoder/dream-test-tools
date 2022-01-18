
import asyncio, time, os
import Byond, OpenDream, ClopenDream

from DTT import App
import test_runner

class Main(App):
    async def run(self, test_dir):
        installs = [ 
            {'platform':'byond','install_id':'default'}, 
            {'platform':'opendream','install_id':'default'},
            {'platform':'clopendream','install_id':'currentdev', 'byond_install_id':'default'} 
        ]

        start_time = time.time()
        pending_tasks = []
        for config in test_runner.list_all_tests(self.config, test_dir):
            for install in installs:
                config['test.platform'] = install['platform']
                config['test.install_id'] = install['install_id']
                test_runner.get_test_info(config, 'curated')
                test_runner.copy_test(config)
                pending_tasks.append( asyncio.create_task( test_runner.test_install(config.copy(), install) ) )
                if len(pending_tasks) > 16:
                    await asyncio.gather( *pending_tasks )
                    pending_tasks = []
        await asyncio.gather( *pending_tasks )
        print(f"{time.time()-start_time}")
        os.system('stty sane')

main = Main()
asyncio.run( main.run(main.config['tests.dirs.input'] / 'dm') )