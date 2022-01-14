
import asyncio

from DTT import App
import test_runner

class Main(App):
    async def run(self, test_dir):
        test_report = test_runner.TestReport({'platform':'byond','install_id':'default'}, {'platform':'opendream','install_id':'default'})
        for i, test_file_path in enumerate(test_runner.list_all_tests(self.config, test_dir)):
            config = self.config.branch( str(i) )
            await test_runner.read_single_test(config, config['tests_dir'], test_file_path, self.test_output_dir)
            result = test_report.compare( config )

        with open( self.test_output_dir / 'reports' / f"{test_report.id1}.{test_report.id2}", "w") as f:
            f.write( test_report.print() )

main = Main()
asyncio.run( main.run(main.config['tests_dir'] / 'dm') )