
import asyncio, sys, json

from DTT import App
import test_runner

# python3.8 test_curation_report.py compile byond.default opendream.default
# python3.8 test_curation_report.py compare clopendream.currentdev

class Main(App):
    async def run(self, test_dir):
        installs = []
        for arg in sys.argv[2:]:
            parsed_arg = arg.split(".")
            install = {'platform':parsed_arg[0], 'install_id':parsed_arg[1]}
            if install['platform'] == 'clopendream':
                install['byond_install_id'] = 'default'
            installs.append( test_runner.load_install(self.config, install) )

        if sys.argv[1] == 'compile':
            install1 = test_runner.load_install(self.config, installs[0])
            install2 = test_runner.load_install(self.config, installs[1])
            test_report = test_runner.CompileReport(installs[0],installs[1])
            for i, config in enumerate(test_runner.list_all_tests(self.config, test_dir)):
                test_report.add_result( config.branch(str(i)) )
            with open( config['tests.dirs.output'] / 'reports' / f"{test_report.install1['id']}-{test_report.install2['id']}-full.html", "w") as f:
                f.write( test_report.get_report() )
            with open( config['tests.dirs.output'] / 'reports' / f"{test_report.install1['id']}-{test_report.install2['id']}-summary.json", "w") as f:
                json.dump( test_report.get_result_summary(), f )

        elif sys.argv[1] == 'compare':
            install1 = test_runner.load_install(self.config, {'platform':'clopendream','install_id':'currentdev'})
            test_report = test_runner.CompareReport(installs[0])
            for i, config in enumerate(test_runner.list_all_tests(self.config, test_dir)):
                test_report2.add_result( config.branch(str(i)) )
            with open( config['tests.dirs.output'] / 'reports' / f"{test_report.install['id']}.html", "w") as f:
                f.write( test_report.get_report() )

        else:
            raise Exception("unknown command")

main = Main()
asyncio.run( main.run(main.config['tests.dirs.input'] / 'dm') )