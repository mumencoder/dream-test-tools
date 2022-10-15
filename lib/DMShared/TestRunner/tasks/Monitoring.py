
from .common import *

class Monitoring(object):
    @staticmethod
    def register_metrics(env):
        env.attr.test_counter = 0
        async def count_test(tenv):
            env.attr.test_counter += 1
        env.event_handlers["test.complete"] = count_test

        async def report_counter(penv, senv):
            start_time = time.time()
            while env.attr.scheduler.running:
                penv.attr.self_task.log( env.attr.test_counter / (time.time() - start_time) )
                await asyncio.sleep(60.0)

        return Shared.Task(env, report_counter, ptags={'action':'report_counter'}, background=True)
    