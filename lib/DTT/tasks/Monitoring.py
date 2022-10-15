
from .common import *

class Monitoring(object):
    @staticmethod
    def register_metrics(env):
        env.attr.test_counter = 0
        async def count_test(tenv):
            env.attr.test_counter += 1
        env.event_handlers["test.complete"] = count_test

        async def report_counter(env):
            env.attr.workflow.open( {'action':'report_counter'} )
            start_time = time.time()
            while env.attr.scheduler.running:
                env.attr.task.log( env.attr.test_counter / (time.time() - start_time) )
                await asyncio.sleep(30.0)

        env.attr.scheduler.add( report_counter(env), background=True )
    