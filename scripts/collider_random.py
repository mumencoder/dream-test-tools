
import asyncio, time, shutil
import collections
import Shared, Byond, OpenDream
import dream_collider
import test_runner
from DTT import App

class Main(App):
    def __init__(self):
        super().__init__()
        self.opendream_results = {"retcodes":{}}
        self.byond_results = {"retcodes": {}}

        self.results = collections.defaultdict(int)

    async def handle_opendream_compile(self, config, process):
        self.opendream_results['retcodes'][config['test.id']] = process.returncode

    async def handle_byond_compile(self, config, process):
        self.byond_results['retcodes'][config['test.id']] = process.returncode

    async def collide(self, config):
        builder = dream_collider.builders.FullRandomBuilder()
        test_id = f'gentest-{Shared.Random.generate_string(8)}'
        config['test.id'] = test_id
        config['test.base_dir'] = self.test_output_dir / 'brrr' / config['test.id']
        config['test.text'] = str(builder.test(config, 4))
        config['test.builder'] = builder

    async def generate_test(self):
        self.results["generation_attempts"] += 1
        config = self.config
        try:
            await self.collide(config)
            with open(config['test.base_dir'] / 'base_test.dm', "w") as f:
                f.write( config['test.text'] )
            await config.send_event('test.generated', config)
        except Exception:
            self.results["generation_exception"] += 1


    async def redo_test(self, test_id):
        config = self.config.branch(test_id)
        config['test.id'] = test_id
        config['test.base_dir'] = self.test_output_dir / 'saved' / config['test.id']
        with open(config['test.base_dir'] / 'base_test.dm', "r") as f:
            config['test.text'] = f.read()
        await config.send_event('test.generated', config)

    async def test_byond(self, test_config):
        config = self.config.merge(test_config)
        final_text = test_runner.test_prep.wrap_test(config, config['test.text'])
        config = await test_runner.test_prep.write_test(config, final_text)
        await test_runner.byond.compile(config)

    async def test_opendream(self, test_config):
        config = self.config.merge(test_config)
        final_text = test_runner.test_prep.wrap_test(config, config['test.text'])
        config = await test_runner.test_prep.write_test(config, final_text)
        await test_runner.opendream.compile(config)

    async def compare_test(self, test_config):
        await self.test_byond(test_config, config['test.text'])
        await self.test_opendream(test_config, config['test.text'])

        if self.byond_results['retcodes'][config['test.id']] == 0:
            byond_compile = True
        else:
            byond_compile = False

        if self.opendream_results['retcodes'][config['test.id']] == 0:
            opendream_compile = True
        else:
            opendream_compile = False

        if byond_compile is False:
            return 
        if byond_compile is not opendream_compile:
            print(config['test.id'])
        
    def initialize(self):
        Byond.Install.set_current(self.config, self.config['byond.version'])
        self.config.event_handlers['test.compile.byond.result'] = self.handle_byond_compile

        OpenDream.Install.set_current(self.config, self.config['opendream.build.id'])
        self.config.event_handlers['test.compile.opendream.result'] = self.handle_opendream_compile

    async def run(self):
        self.initialize()

        async def handle_test(config):
            config['test.platform'] = 'byond'
            await self.test_byond(config)
            retcode = self.byond_results['retcodes'][config['test.id']]
            #print( config['test.text'] )
            #print( "-------------" )

            compile_success = retcode == 0

            if compile_success != config['test.builder'].should_compile:
                print("---")
                print( f"{config['test.id']}, compile_success={compile_success}, should_compile={config['test.builder'].should_compile}" )
                print( f"{config['test.builder'].modified_validations}")
                shutil.move( config['test.base_dir'], self.test_output_dir / 'saved' / config['test.id'])
            else:
                shutil.rmtree( config['test.base_dir'] )

        self.config.event_handlers['test.generated'] = handle_test
        tests = 0
        start_time = time.time()
        while True:
            tests += 1
            if tests in [10, 100, 1000]:
                print(f"{tests} tests in {time.time() - start_time} secs")
            config = self.config.branch("!")
            await self.generate_test()
            if (tests+1) % 1000 == 0:
                print("--------------------")
                print( config['test.text'] )
                print(self.results)
            config = config.pop()

try:
    asyncio.run( Main().run() )
except KeyboardInterrupt:
    pass
    