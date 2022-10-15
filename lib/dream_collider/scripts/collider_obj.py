
import dream_collider
from DTT import App

class Main(App):
    def __init__(self):
        super().__init__()

    async def collide(self, env):
        builder = dream_collider.builders.FullRandomBuilder(env)

    async def save_test(self, env):
        env.test.id = f'{Shared.Random.generate_string(8)}'
        config['test.text'] = str(builder.test(config, 32))
        config['test.builder'] = builder

    async def handle_test(self, config):
        start_time = time.time()
        config['test.install'] = test_runner.load_install(config, install)
        config['test.base_dir'] = config['tests.dirs.output'] / 'brrr' / config['test.id'] / config['test.install']["id"]
        test_runner.copy_test(config)
        await test_runner.test_install(config.copy(), install)
        self.install_time[config['test.install']['id']] += time.time() - start_time

        if config['test.install']["platform"] == 'byond':
            rcode_path = config['test.base_dir'] / "compile.returncode.txt"
            if os.path.exists(rcode_path):
                with open(rcode_path) as f:
                    byond_compiled = int(f.read()) == 0
            else:
                raise Exception("no return code")

        if byond_compiled != config['test.builder'].should_compile:
            summary = {'byond_compiled':byond_compiled, 'should_compile':config['test.builder'].should_compile, 'notes':config['test.builder'].notes }
            print(summary)

            save_dir = config['tests.dirs.output']/ 'saved' / config['test.id']
            shutil.move( str(config['tests.dirs.output'] / 'brrr' / config['test.id']), save_dir )

            with open(save_dir / 'notes.json', "w") as f:
                json.dump( summary, f )

            self.saved += 1
        else:
            shutil.rmtree( config['tests.dirs.output'] / 'brrr' / config['test.id'] )

    async def do_test(self):
        start_time = time.time()
        tenv = Shared.Env.branch(env)
        await self.collide(tenv)
        await self.save_test(tenv)
        for ienv in self.install_envs:
            tienv = Shared.Env.merge(tenv, ienv, branch=True)
            await self.handle_test(tienv)

    def initialize(self):
        pass

    async def run(self):
        self.initialize()
        self.running = True
        while self.running:
            self.do_test(env)

try:
    asyncio.run( Main().run() )
except KeyboardInterrupt:
    os.system('stty sane')

#            if self.saved >= 10:
#                self.print_progress()
#                break
#            self.tests += 1
#            if self.tests in [10, 100, 1000, 10000]:
#                self.print_progress()
#            if self.tests > 10000 and self.tests % 10000 == 0:
#                self.print_progress()
