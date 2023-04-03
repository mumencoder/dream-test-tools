
from .imports import *

### tasks
def new_task(fn, *args, **kwargs):
    pending_tasks.append( (fn, args, kwargs) )

def async_thread_launch():
    asyncio.run( async_thread_main() )

async def async_thread_main():
    global pending_tasks, tasks
   
    while True:
        for fn, args, kwargs in pending_tasks:
            tasks.add( asyncio.create_task( fn(*args, **kwargs) ) )
        pending_tasks = []

        try:
            for co in asyncio.as_completed(tasks, timeout=0.1):
                await co
        except TimeoutError:
            pass
        
        remaining_tasks = set()
        for task in tasks:
            if not task.done():
                remaining_tasks.add( task )
            else:
                pass
        tasks = remaining_tasks
