
class ProcessManager(object):
    def __init__(self, config):
        self.max_memory_usage = -1
        self.memory_limit = config['process.memory_limit']

    async def cleanup(self):
        if self.state == "kill":
            self.process.kill()
            await asyncio.wait_for(self.process.wait(), None)
        self.finish_time = time.time()

    def is_wait_state(self):
        if self.state == "kill":
            return False
        if self.process.returncode is not None:
            return False
        return True

    async def wait(self):
        while self.is_wait_state():
            try:
                await asyncio.wait_for(self.process.wait(), timeout=self.update_delay)
            except asyncio.exceptions.TimeoutError:
                pass
            for update in self.updates:
                update(self)

    def update(self, process):
        pinfo = process.find_by_tag()
        if len(pinfo) == 0:
            return
        if len(pinfo) > 1:
            raise Exception("non unique process")
        pinfo = pinfo[0]
        try:
            if self.memory_limit is not None and pinfo.memory_full_info().uss > self.memory_limit:
                process.state = "kill"
                print("warning: memory limit reached")
                return
            self.max_memory_usage = max( self.max_memory_usage, pinfo.memory_full_info().uss)
        except psutil.NoSuchProcess:
            pass