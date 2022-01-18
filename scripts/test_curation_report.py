
import asyncio

from DTT import App
import test_runner

class Main(App):
    async def run(self, test_dir):
        test_report1 = test_runner.CompileReport({'platform':'byond','install_id':'default'}, {'platform':'opendream','install_id':'default'})
        test_report2 = test_runner.CompareReport({'platform':'clopendream','install_id':'currentdev'})

        for i, config in enumerate(test_runner.list_all_tests(self.config, test_dir)):
            test_report1.add_result( config.branch(str(i)) )
            test_report2.add_result( config.branch(str(i)) )

        with open( config['tests.dirs.output'] / 'reports' / f"{test_report1.id1}-{test_report1.id2}.html", "w") as f:
            f.write( test_report1.get_report() )
        with open( config['tests.dirs.output'] / 'reports' / f"{test_report2.id}.html", "w") as f:
            f.write( test_report2.get_report() )

main = Main()
asyncio.run( main.run(main.config['tests.dirs.input'] / 'dm') )