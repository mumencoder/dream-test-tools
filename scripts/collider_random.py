
import asyncio, time, shutil, os
import collections
import Shared, Byond, OpenDream, ClopenDream
import dream_collider
import test_runner
from DTT import App

class Main(App):
    def __init__(self):
        super().__init__()

    def initialize(self):
        self.error_factor = 1.00
        self.stats = collections.defaultdict(int)
        self.start_time = time.time()
        self.install_time = collections.defaultdict(float)

        self.installs = [ 
            {'platform':'byond','install_id':'default'}, 
        ]

    async def collide(self, config):
        builder = dream_collider.builders.FullRandomBuilder(config)
        test_id = f'gentest-{Shared.Random.generate_string(8)}'
        config['test.id'] = test_id
        config['test.source_file'] = config['tests.dirs.output'] / 'brrr' / config['test.id'] / 'test.dm'
        config['test.text'] = str(builder.test(config, 8))
        config['test.builder'] = builder

    async def generate_test(self):
        config = self.config
        await self.collide(config)
        with open(config['test.source_file'], "w") as f:
            f.write( config['test.text'] )
        await config.send_event('test.generated', config)

    async def handle_test(self, config):
        self.stats['total'] += 1
        for install in self.installs:
            start_time = time.time()
            config['test.platform'] = install['platform']
            config['test.install_id'] = install['install_id']
            config['test.test_runner'] = f"{config['test.platform']}.{config['test.install_id']}"
            config['test.base_dir'] = config['tests.dirs.output'] / 'brrr' / config['test.id'] / config['test.test_runner']
            test_runner.copy_test(config)
            await test_runner.test_install(config.copy(), install)
            self.install_time[config['test.test_runner']] += time.time() - start_time

            if config['test.platform'] == 'byond':
                rcode_path = config['test.base_dir'] / "compile.returncode.txt"
                if os.path.exists(rcode_path):
                    with open(rcode_path) as f:
                        byond_compiled = int(f.read()) == 0
                else:
                    raise Exception("no return code")

            if config['test.builder'].should_compile:
                self.stats['should_compile'] += 1

            if byond_compiled != config['test.builder'].should_compile:
                print( "---" )
                print( f"{config['test.id']}" )
                print( f"byond_compiled={byond_compiled}, should_compile={config['test.builder'].should_compile}" )
                print( f"{config['test.builder'].notes}" )
                shutil.move( config['tests.dirs.output'] / 'brrr' / config['test.id'], config['tests.dirs.output']/ 'saved' / config['test.id'] )
                self.saved += 1
            else:
                self.stats['generator_agree'] += 1
                shutil.rmtree( config['tests.dirs.output'] / 'brrr' / config['test.id'] )

    def adjust_error_factor(self):
        should_compile_rate = self.stats['should_compile'] / max(1,self.stats['total'])
        if should_compile_rate < 0.8:
            self.error_factor /= 1.05
        else:
            self.error_factor *= 1.05

    def print_progress(self):
        print("===============================")
        print(f"{self.tests} tests in {time.time() - self.start_time} secs")
        pct_stats = {k:v / self.stats['total'] for k,v in self.stats.items()}
        print(pct_stats)

    async def run(self):
        self.initialize()
        self.running = True
        self.saved = 0

        self.config.event_handlers['test.generated'] = self.handle_test
        self.tests = 0
        self.start_time = time.time()
        while True:
            if self.saved >= 10:
                self.print_progress()
                break
            self.tests += 1
            if self.tests in [10, 100, 1000, 10000]:
                self.print_progress()
            config = self.config.branch("!")
            self.adjust_error_factor()
            self.config['test.error_factor'] = self.error_factor
            await self.generate_test()
            config = config.pop()
        os.system('stty sane')

try:
    asyncio.run( Main().run() )
except KeyboardInterrupt:
    pass
