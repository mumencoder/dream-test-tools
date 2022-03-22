
import os, asyncio

class ResourceTracker(object):
    def __init__(self, limit=None):
        self.limit = limit
        self.resources = []
        self.lock = asyncio.Lock()

        i = 0
        while True:
            if self.limit is not None and len(self.resources) >= self.limit:
                break
            data = self.resource_data(i)
            if not self.check_exist(data):
                break
            self.resources.append( {'available':True, 'data':data } )
            i += 1

    def resource_data(self, i):
        raise NotImplemented()

    def check_exist(self, data):
        raise NotImplemented()

    async def acquire(self):
        async with self.lock:
            for resource in self.resources:
                if resource['available'] is True:
                    resource['available'] = False
                    return resource

            create = False
            if self.limit is None:
                create = True
            elif len(self.resources) < self.limit:
                create = True
            if create:
                resource = self.add_resource()
                resource['available'] = False
                return resource
            return None            

    def release(self, resource):
        resource['available'] = True

    def add_resource(self):
        i = 0
        while True:
            data = self.resource_data(i)
            if not self.check_exist(data):
                self.make_exist(data)
                resource = {'available':True, 'data':data}
                self.resources.append( resource )
                return resource
            i += 1

class OpenDreamRepoResource(ResourceTracker):
    def __init__(self, env, limit=None):
        self.env = env
        super().__init__(limit=limit)

    def resource_data(self, i):
        return {"id":f'shared.{i}', "path": self.env.attr.opendream.dirs.sources / f'shared.{i}'}

    def check_exist(self, data):
        return os.path.exists(data["path"])

    def make_exist(self, data):
        data["path"].ensure_folder()
