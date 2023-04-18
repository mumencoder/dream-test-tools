
from .imports import *

def load_config(env, config):
    warnings = []
    errors = []

    def assign_value(resource, prefix, type_define):
        env_prefix = env.attr
        for segment in prefix:
            env_prefix = getattr( env_prefix, segment )
        for k, v in resource.items():
            if k in type_define:
                if type(type_define[k]) is dict:
                    assign_value( v, prefix + tuple([k]), type_define[k] )
                else:
                    match type_define[k]:
                        case "path":
                            v = Shared.Path(v)
                        case "int":
                            v = int(v)
                        case "str":
                            v = str(v)
                        case _:
                            warnings.append( {"type":"resource:unknown_define_type", "resource":resource_name, "key":k})     
                            continue
                    setattr(env_prefix, k, v)

    for resource_name, resource in config['resources'].items(): 
        prefix = tuple([resource_name])
        if 'type' not in resource:
            errors.append( {"type":"resource:type_field_missing", "resource":resource_name} )
            continue
        resource_type = resource['type']
        if resource_type not in config['types']:
            errors.append( {"type":"resource:type_define_missing", "resource":resource_name} )
            continue
        type_define = config['types'][resource_type]
        assign_value(resource, prefix, type_define)
    return {"warnings":warnings, "errors":errors}

def load_paths(env):
    for resource_name, resource in env.attr.config_file['resources'].items():
        if resource['type'] == "path":
            env.set_attr(f'.{resource_name}', env.attr.config.get_attr(f'.{resource_name}.value') )
class EnvTracker(object):
    def __init__(self, env, title, update_existing=True):
        self.env = env
        self.title = title
        self.seen = set()
        if update_existing:
            self.update()

    def update(self):
        self.seen = set()
        for prop in self.env.unique_properties():
            self.seen.add(prop)

    def print_local(self):
        print(f"=== {self.title} local")
        for prop in self.env.local_properties():
            print(prop, type(self.env.get_attr(prop)))

    def print(self, count): 
        print(f"=== {self.title} {count}")
        for prop in self.env.unique_properties():
            if prop in self.seen:
                continue
            print(prop, type(self.env.get_attr(prop)))
        for seen in self.seen:
            if not self.env.attr_exists(seen):
                print(f"{prop} - removed")
        self.update()

def env_tod(env, d, props=None):
    if props is None:
        props = env.unique_properties()
    for prop in props:
        d[prop] = env.get_attr(prop)
    return d

def env_fromd(env, d):
    for k, v in d.items():
        env.set_attr(k, v)
    return env

def base_env():
    root_env = Shared.Environment()

    root_env.attr.shell.env = os.environ

    config_env = Shared.Environment()

    if os.path.exists('/DTT/resources/local/server_config.yaml'):
        with open('/DTT/resources/local/server_config.yaml', "r") as f:
            config_file = yaml.load( f, yaml.Loader )
    else:
        raise Exception("cannot read config")

    load_config(config_env, config_file)

    root_env.attr.config = config_env
    root_env.attr.config_file = config_file

    load_paths(root_env)

    root_env.attr.collider.build_checker = DreamCollider.ASTChecker()
    root_env.attr.collider.build_checker.load_all()

    return root_env

import DreamCollider