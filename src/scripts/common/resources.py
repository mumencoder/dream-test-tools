
from .imports import *

def iter_resources(resources, prefix=""):
    for name, resource in resources.items():
        if type(resource) is dict and 'type' in resource:
            if resource['type'] == "Composite":
                for k,v in resource.items():
                    if k == 'type':
                        continue
                    yield from iter_resources(resource[k], prefix=prefix + name + ".")                
            else:
                yield (prefix + name, resource)

def parse_csv(l):
    return [ s.strip() for s in l.split(',') if s.strip() != "," ]