
import os, sys
import Shared

def setup(config):
    config['storage_dir'] = Shared.Path( os.path.expanduser('~/dream-storage') )
    config['source_dir'] = Shared.Path( os.path.expanduser('~/dream-storage/source/dream-test-tools') )
    config['tmp_dir'] = Shared.Path( '/tmp/dream' ) 

    config['tests.dirs.input'] = config['source_dir'] / "tests"
    config['tests.dirs.output'] = config['storage_dir'] / 'tests'
    config['tests.dirs.resources'] = config['source_dir'] / "tests" / "resources"

    base_dir = config['storage_dir'] / 'byond'
    config['byond.dirs.downloads'] = base_dir / 'downloads'
    config['byond.dirs.installs'] = base_dir / 'installs'

    base_dir = config['storage_dir'] / 'opendream'
    config['opendream.dirs.builds'] = base_dir / 'builds'

    base_dir = config['storage_dir'] / 'clopendream'
    config['clopendream.dirs.builds'] = base_dir / 'builds'
    config['clopendream.dirs.output'] = base_dir / 'output'

    base_dir = config['storage_dir'] / 'SS13'
    config['ss13.dirs.repos'] = base_dir / 'repos'
    config['ss13.repo_infos'] = [
        {'name':'tgstation-OD', 'url':'https://github.com/wixoaGit/tgstation'},
        {'name':'Baystation12', 'url':'https://github.com/Baystation12/Baystation12'},
        {'name':'BeeStation', 'url':'https://github.com/BeeStation/BeeStation-Hornet'}, 
        {'name':'goonstation', 'url':'https://github.com/goonstation/goonstation'},
        {'name':'Hippiestation', 'url':'https://github.com/HippieStation/HippieStation', 'major':'511', 'dme':'hippiestation.dme'},
        {'name':'NTStation', 'url':'https://github.com/NTStation/NTstation13'},
        {'name':'NTStation-od1', 'url':'https://github.com/ike709/NTstation13', 'branch':'od_minimalmods'},
        {'name':'Paradise', 'url':'https://github.com/ParadiseSS13/Paradise'},
        {'name':'Paradise-od1', 'url':'https://github.com/ike709/Paradise', 'branch':'od_yeet_just_compile'},
        {'name':'tgstation', 'url':'https://github.com/tgstation/tgstation'},
        {'name':'vgstation', 'url':'https://github.com/vgstation-coders/vgstation13'},
        {'name':'Yogstation', 'url':'https://github.com/yogstation13/Yogstation'}
    ]

    config['process.stdout'] = sys.stdout
    config['process.stderr'] = sys.stderr
    config['process.tag'] = False

    return config

def defaults(config):
    config['byond.installs'] = {
        'default': {'type':'web_official', 'version':'514.1575' }
    }
    
    config['opendream.installs'] = {
        'default' : {'type':'repo', 'url':'https://github.com/wixoaGit/OpenDream', 'branch':'master' }
    }

    config['clopendream.installs'] = {
        'default' : {'type':'repo', 'url':'https://github.com/mumencoder/Clopendream-parser', 'branch':'main'}
    }

    config['byond.install.id'] = 'default'
    config['opendream.install.id'] = 'default'
    config['clopendream.install.id'] = 'default'

    config['ss13.repo_ids'] = ['NTStation-od1']
