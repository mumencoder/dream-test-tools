
import os, sys
import Shared

def setup_roots(env):
    env.attr.dirs.root = Shared.Path( os.path.expanduser('/DTT/data') )
    env.attr.dirs.source = Shared.Path( os.path.expanduser('/DTT/src') )
    env.attr.dirs.ramdisc = Shared.Path( '/DTT/data/scratch' ) 
    env.attr.dirs.tmp = Shared.Path( '/tmp/dream-test-tools' )
    
    env.attr.dirs.state = env.attr.dirs.root / 'state'

    env.attr.process.stdout = sys.stdout
    env.attr.process.stderr = sys.stderr
    env.attr.process.tag = False

def setup_tests(env):
    env.attr.tests.dirs.dm_files = env.attr.dirs.source / "tests" / "dm"
    env.attr.tests.dirs.resources = env.attr.dirs.source / "tests" / "resources"
    env.attr.tests.dirs.output = env.attr.dirs.root / "tests"
    env.attr.tests.dirs.reports = env.attr.dirs.root / "reports"

def setup_byond(env):
    root_dir = env.attr.byond.dirs.root = env.attr.dirs.root / 'byond'
    env.attr.byond.dirs.downloads = root_dir / 'downloads'
    env.attr.byond.dirs.installs = root_dir / 'installs'

def setup_opendream(env):
    root_dir = env.attr.opendream.dirs.root = env.attr.dirs.root / 'opendream'
    env.attr.opendream.dirs.sources = root_dir / 'sources'
    env.attr.opendream.dirs.installs = root_dir / 'installs'

def setup_clopendream(env):
    root_dir = env.attr.clopendream.dirs.root = env.attr.dirs.root / 'clopendream'
    env.attr.clopendream.dirs.sources = root_dir / 'sources'
    env.attr.clopendream.dirs.installs = root_dir / 'installs'

def setup_ss13(env):
    root_dir = env.attr.ss13.dirs.root = env.attr.dirs.root / 'SS13'
    env.attr.ss13.dirs.installs = root_dir / 'installs'

def setup_defaults(env):
    env.attr.byond.installs = {
        'main': {'type':'web_official', 'version':'514.1575' }
    }
    
    env.attr.ss13.sources = {
        'tgstation-OD': {'type':'repo', 'url':'https://github.com/wixoaGit/tgstation'},
        'Baystation12': {'type':'repo', 'url':'https://github.com/Baystation12/Baystation12'},
        'BeeStation': {'type':'repo', 'url':'https://github.com/BeeStation/BeeStation-Hornet'}, 
        'goonstation': {'type':'repo', 'url':'https://github.com/goonstation/goonstation'},
        'Hippiestation': {'type':'repo', 'url':'https://github.com/HippieStation/HippieStation', 
            'byond_version':'511', 'dme':'hippiestation.dme'},
        'NTStation': {'type':'repo', 'url':'https://github.com/NTStation/NTstation13'},
        'NTStation-od1': {'type':'repo', 'url':'https://github.com/ike709/NTstation13', 
            'branch':{'remote':'origin', 'name':'od_minimalmods'}},
        'Paradise': {'type':'repo', 'url':'https://github.com/ParadiseSS13/Paradise'},
        'Paradise-od1': {'type':'repo', 'url':'https://github.com/ike709/Paradise', 
            'branch':{'remote':'origin', 'name':'od_yeet_just_compile'}},
        'tgstation': {'type':'repo', 'url':'https://github.com/tgstation/tgstation'},
        'vgstation': {'type':'repo', 'url':'https://github.com/vgstation-coders/vgstation13'},
        'Yogstation': {'type':'repo', 'url':'https://github.com/yogstation13/Yogstation'}
    }
