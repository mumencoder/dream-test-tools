
from ..imports import *
from ..misc import *

from .builder import *
from .tester import *
from .filter import *
from .install import *
from .results import *

def load_churn_info(config, envo):
    envo.attr.churn.builders = parse_csv(config.builder)
    envo.attr.churn.testers = parse_csv(config.tester)
    envo.attr.churn.filters = parse_csv(config.filter)
    envo.attr.churn.filter_test_ids = collections.defaultdict(list)
    for filter_name in envo.attr.churn.filters:
        if not os.path.exists( config.result_dir / filter_name ):
            continue
        for test_id in os.listdir( config.result_dir / filter_name ):
            envo.attr.churn.filter_test_ids[filter_name].append( test_id )
    envo.attr.churn.filter_test_ids = dict(envo.attr.churn.filter_test_ids)
    
def load_churn(env, id):
    env.attr.churn.config = env.attr.config.prefix(f".{id}")
    env.attr.churn.builders = { s:globals()[f'builder_{s}'] for s in parse_csv(env.attr.churn.config.builder) }
    env.attr.churn.testers = { s: globals()[f'tester_{s}'] for s in parse_csv(env.attr.churn.config.tester) }
    env.attr.churn.filters = { s: globals()[f'filter_{s}'] for s in parse_csv(env.attr.churn.config.filter) }

def churn_count_existing(env):
    return len(os.listdir( env.attr.churn.config.result_dir ))

def churn_trim_tests(env, n):
    test_ids = os.listdir( env.attr.churn.config.result_dir )
    count = len(test_ids)
    print(f"trimming {count} tests")
    if count > 100000:
        keeps = test_ids[0:100000]
        for test_id in test_ids:
            if test_id not in keeps:
                shutil.rmtree( env.attr.churn.config.result_dir / test_id )

async def churn_run(churn_id):
    env = base_env()
    load_churn(env, churn_id)

    print( list(env.unique_properties() ))
    if hasattr(env.attr.churn.config, 'benv'):
        env.attr.benv = env.branch()
        load_byond_install(env.attr.benv, env.attr.churn.config.benv )
    if hasattr(env.attr.churn.config, 'oenv'):
        env.attr.oenv = env.branch()
        load_opendream_install(env.attr.oenv, env.attr.churn.config.oenv )

    filters_finished = set()
    while True:
        tenv = env.branch()

        if len(tenv.attr.churn.filters) == len(filters_finished):
            return
        
        for builder in tenv.attr.churn.builders.values():
            await builder(tenv)
        generate_ast(tenv)
        tokenize_ast(tenv)
        unparse_tokens(tenv)
        for tester in tenv.attr.churn.testers.values():
            await tester(tenv)
        for filter_name, filter_fn in tenv.attr.churn.filters.items():
            if os.path.exists( tenv.attr.churn.config.result_dir / filter_name ):
                if len( os.listdir( tenv.attr.churn.config.result_dir / filter_name ) ) > 100:
                    filters_finished.add( filter_name )
            if filter_name in filters_finished:
                continue
            if await filter_fn(tenv):
                data = save_test(tenv)
                test_id = Shared.Random.generate_string(24)
                with open( tenv.attr.churn.config.result_dir / filter_name / test_id, "wb" ) as f:
                    f.write( data )
