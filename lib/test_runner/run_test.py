
import test_runner

async def test_all_platforms(config):
    await test_runner.byond.do_test( config.branch('byond') )
    await test_runner.opendream.do_test( config.branch('opendream') )
    await test_runner.clopendream.do_test( config.branch('clopendream') )