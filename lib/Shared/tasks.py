
import asyncio 

import Shared

class CountedResource(object):
    def __init__(self, n):
        self.n = n
        self.counts = set()
    
    async def acquire(self, env):
        while len(self.counts) >= self.n:
            await asyncio.sleep(0.2)
        self.counts.add( env.attr.wf.name )

    def release(self, env):
        self.counts.remove( env.attr.wf.name )

