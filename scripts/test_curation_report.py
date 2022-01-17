
import asyncio

from DTT import App
import test_runner

class Main(App):
    async def run(self, test_dir):
        test_report = test_runner.TestReport({'platform':'byond','install_id':'default'}, {'platform':'opendream','install_id':'default'})
        for i, config in enumerate(test_runner.list_all_tests(self.config, test_dir)):
            result = test_report.compile_result( config.branch(str(i)) )

        with open( config['tests.dirs.output'] / 'reports' / f"{test_report.id1}-{test_report.id2}", "w") as f:
            f.write( test_report.compile_report() )

main = Main()
asyncio.run( main.run(main.config['tests.dirs.input'] / 'dm') )