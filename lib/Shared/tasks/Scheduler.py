
import asyncio

import Shared

class Scheduler(object):
    
    def fork(env, coll_var, iter_var, task, limit=None):
        async def task_loop():
            subtasks = set()
            it = iter(senv.get_attr(coll_var))

            try:
                rest_interval = 0.5
                while True:
                    while len(subtasks) < limit:
                        subenv = env.branch()
                        subenv.set_attr(iter_var, next(it))
                        new_subtask = asyncio.create_task( task(subenv) )
                        subtasks.add(new_subtask)
                    for subtask in asyncio.as_completed( subtasks, timeout=1.0 ):
                        await task
                    for subtask in list(subtasks):
                        if task.done():
                            subtasks.remove(subtask)
                    if len(subtasks) > 0:
                        await asyncio.sleep(rest_interval)
                        env.attr.workflow.log( f"rested {rest_interval} remaining_tasks: {len(subtasks)} / {limit}" )
                    else:
                        break
                    if len(subtasks) > limit / 2:
                        rest_interval *= 1.2
                    if len(subtasks) < limit / 2:
                        rest_interval /= 1.2
                    rest_interval = min(rest_interval, 10.0)
            except KeyboardInterrupt:
                raise
            except asyncio.exceptions.CancelledError:
                return
            except GeneratorExit:
                return
            except:
                env.attr.workflow.log( f"subtask exception: {traceback.format_exc()}")

        return asyncio.create_task( task_loop() )
