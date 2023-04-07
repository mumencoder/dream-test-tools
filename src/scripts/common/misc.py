
from .tasks import *
from .imports import *

class Counter(object):
    def __init__(self):
        self.c = 0
        self.visible_states = [2 ** x for x in range(0,11)]
        self.visible = False

    def inc(self, n=1):
        self.c += n
        self.update_state()
        
    def update_state(self):
        if self.c in self.visible_states or self.c % self.visible_states[-1] == 0:
            self.visible = True
        else:
            self.visible = False

    def state(self):
        return self.visible
    
def parse_csv(l):
    return [ s.strip() for s in l.split(',') if s.strip() != "," ]

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