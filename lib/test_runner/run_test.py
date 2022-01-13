
import Byond, OpenDream
import test_runner

async def test_install(config, install):
    if install["platform"] == 'byond':
        Byond.Install.set_current(config, install['install_id'])
        await test_runner.byond.do_test( config.branch('byond') )
    elif install["platform"] == 'opendream':
        OpenDream.Install.set_current(config, install['install_id'])
        await test_runner.opendream.do_test( config.branch('opendream') )
    else:
        raise Exception(f"unknown platform {install['platform']}")