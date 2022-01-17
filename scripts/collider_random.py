
import asyncio, time, shutil
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

        Byond.Install.set_current(self.config, self.config['byond.install.id'])
        OpenDream.Install.set_current(self.config, self.config['opendream.install.id'])
        ClopenDream.Install.set_current(self.config, self.config['clopendream.install.id'])

    async def collide(self, config):
        builder = dream_collider.builders.FullRandomBuilder(config)
        test_id = f'gentest-{Shared.Random.generate_string(8)}'
        config['test.id'] = test_id
        config['test.base_dir'] = config['tests.dirs.output'] / 'brrr' / config['test.id']
        config['test.text'] = str(builder.test(config, 8))
        config['test.builder'] = builder

    async def generate_test(self):
        config = self.config
        await self.collide(config)
        with open(config['test.base_dir'] / 'base_test.dm', "w") as f:
            f.write( config['test.text'] )
        await config.send_event('test.generated', config)

    async def redo_test(self, test_id):
        config = self.config.branch(test_id)
        config['test.id'] = test_id
        config['test.base_dir'] = config['tests.dirs.output'] / 'saved' / config['test.id']
        with open(config['test.base_dir'] / 'base_test.dm', "r") as f:
            config['test.text'] = f.read()
        await config.send_event('test.generated', config)

    async def handle_test(self, config):
        await test_runner.test_all_platforms(config)

        # broken until callbacks are fixed
        return 

        retcode = self.byond_results['retcodes'][config['test.id']]
        byond_compiled = retcode == 0
        retcode = self.opendream_results['retcodes'][config['test.id']]
        opendream_compiled = retcode == 0

        self.stats['total'] += 1
        if config['test.builder'].should_compile:
            self.stats['should_compile'] += 1
        if config['test.builder'].should_compile == byond_compiled:
            self.stats['generator_agree'] += 1
        if opendream_compiled == byond_compiled:
            self.stats['opendream_agree'] += 1

        if byond_compiled != opendream_compiled:
            print( "---" )
            print( f"{config['test.id']}" )
            print( f"byond_compiled={byond_compiled}, should_compile={config['test.builder'].should_compile}" )
            print( f"opendream_compiled={opendream_compiled}" )
            print( f"{config['test.builder'].notes}" )
            shutil.move( config['test.base_dir'], config['tests.dirs.output']/ 'saved' / config['test.id'] )
            self.saved += 1
        else:
            shutil.rmtree( config['test.base_dir'] )

    def adjust_error_factor(self):
        should_compile_rate = self.stats['should_compile'] / max(1,self.stats['total'])
        if should_compile_rate < 0.8:
            self.error_factor /= 1.05
        else:
            self.error_factor *= 1.05

    async def run(self):
        self.initialize()
        self.running = True
        self.saved = 0

        self.config.event_handlers['test.generated'] = self.handle_test
        tests = 0
        start_time = time.time()
        while True:
            if self.saved >= 10:
                break
            tests += 1
            if tests in [10, 100, 1000]:
                print(f"{tests} tests in {time.time() - start_time} secs")
            config = self.config.branch("!")
            self.adjust_error_factor()
            self.config['test.error_factor'] = self.error_factor
            await self.generate_test()
            if (tests+1) % 50 == 0:
                print(self.stats['total'], self.error_factor)
                pct_stats = {k:v / self.stats['total'] for k,v in self.stats.items()}
                print(pct_stats)
            config = config.pop()

try:
    asyncio.run( Main().run() )
except KeyboardInterrupt:
    pass
