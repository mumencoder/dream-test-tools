
import asyncio

from DTT import App
import test_runner

class Main(App):
    async def run(self, test_dir):
        install1 = test_runner.load_install(self.config, {'platform':'byond','install_id':'default'})
        install2 = test_runner.load_install(self.config, {'platform':'opendream','install_id':'default'})
        install3 = test_runner.load_install(self.config, {'platform':'clopendream','install_id':'currentdev'})
        test_report1 = test_runner.CompileReport(install1,install2)
        test_report2 = test_runner.CompareReport(install3)

        for i, config in enumerate(test_runner.list_all_tests(self.config, test_dir)):
            test_report1.add_result( config.branch(str(i)) )
            test_report2.add_result( config.branch(str(i)) )

        with open( config['tests.dirs.output'] / 'reports' / f"{test_report1.install1['id']}.{test_report1.install2['id']}.html", "w") as f:
            f.write( test_report1.get_report() )
        with open( config['tests.dirs.output'] / 'reports' / f"{test_report2.install['id']}.html", "w") as f:
            f.write( test_report2.get_report() )

        print(test_report1.get_result_summary())

main = Main()
asyncio.run( main.run(main.config['tests.dirs.input'] / 'dm') )