
import os, sys, mumenrepo as Shared

def base_setup(env, output_dir):
    env = env.branch()
#    env.attr.dirs.output = Shared.Path( os.path.realpath( os.path.join( os.path.dirname(__file__), "..", "..", "output" )) )
    env.attr.dirs.output = Shared.Path( output_dir )
    
    env.attr.shell.env = os.environ
    env.attr.process.stdout = sys.stdout
    env.attr.dirs.tmp = env.attr.dirs.output / 'tmp'

    benv = env.branch()
    benv.attr.version.major = 514
    benv.attr.version.minor = 1589
    benv.attr.install.dir =  env.attr.dirs.output / 'byond' / 'main'

    oenv = env.branch()
    oenv.attr.install.dir =  env.attr.dirs.output / 'opendream' / 'main'

    clenv = env.branch()
    clenv.attr.install.dir = env.attr.dirs.output / 'clopendream' / 'main'

    env.attr.envs.byond = benv
    env.attr.envs.opendream = oenv
    env.attr.envs.clopendream = clenv

    return env