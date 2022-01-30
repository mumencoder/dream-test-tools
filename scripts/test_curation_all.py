
import asyncio, time, os, sys
import Byond, OpenDream, ClopenDream

from DTT import App
import test_runner

# python3.8 test_curation_all.py byond.default opendream.default clopendream.default
# python3.8 test_curation_all.py opendream.default opendream.local-currentdev

class Main(App):
    async def run(self, test_dir):
        installs = []
        for arg in sys.argv[1:]:
            parsed_arg = arg.split(".")
            install = {'platform':parsed_arg[0], 'install_id':parsed_arg[1]}
            if install['platform'] == 'clopendream':
                install['byond_install_id'] = 'default'
            installs.append( test_runner.load_install(self.config, install) )

        start_time = time.time()
        pending_tasks = []
        for config in test_runner.list_all_tests(self.config, test_dir):
            for install in installs:
                config['test.install'] = install
                test_runner.get_test_info(config, 'curated')
                test_runner.copy_test(config)
                pending_tasks.append( asyncio.create_task( test_runner.test_install(config.copy(), install) ) )
                if len(pending_tasks) > 0:
                    await asyncio.gather( *pending_tasks )
                    pending_tasks = []
        await asyncio.gather( *pending_tasks )
        print(f"{time.time()-start_time}")
        os.system('stty sane')

main = Main()
asyncio.run( main.run(main.config['tests.dirs.input'] / 'dm') )