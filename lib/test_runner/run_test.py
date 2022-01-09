
import test_runner

async def run_test(config, test_file, test_output_dir):
    config['test.platform'] = 'byond'
    config = await test_runner.single_fixed_test(config, config['tests_dir'], test_file, test_output_dir)
    await test_runner.byond.compile(config)
    await test_runner.byond.run(config)

    config['test.platform'] = 'opendream'
    config = await test_runner.single_fixed_test(config, config['tests_dir'], test_file, test_output_dir)
    await test_runner.opendream.compile(config)
    await test_runner.opendream.run(config)

    config['test.platform'] = 'clopendream'
    config = await test_runner.single_fixed_test(config, config['tests_dir'], test_file, test_output_dir)
    config['clopendream.output.base_dir'] = config['test.base_dir']
    await test_runner.clopendream.compare(config)
