
from .common import *

class Metadata:
    def load_test(env):
        env.attr.test.metadata_path = env.attr.test.root_dir / 'test.metadata.json'
        if os.path.exists( env.attr.test.metadata_path ):
            with open(env.attr.test.metadata_path, "r") as f:
                md = json.load(f)
                for attr, value in md.items():
                    env.properties[attr] = value

    def save_test(env):
        env.attr.test.metadata_path = env.attr.test.root_dir / 'test.metadata.json'

        md = {}
        for attr in env.unique_properties():
            if attr.startswith( '.test.metadata.' ):
                md[attr] = env.get_attr(attr)

        with open( env.attr.test.metadata_path, "w" ) as f:
            f.write( json.dumps(md) )