
from ...common import *

class PileArchive:
    def load(env, data):
        if "clear_on_load" in data:
            if type(data["clear_on_load"]) is not bool:
                raise Exception("expected bool for clear_on_load") 
            if os.path.exists( data["path"] ) and data["clear_on_load"]:
                shutil.rmtree( data["path"] )
            if os.path.exists( data["tests_path"] ) and data["clear_on_load"]:
                shutil.rmtree( data["tests_path"] )
        env.attr.piles.path = Shared.Path( data["path"] )
        env.attr.piles.tests_path = Shared.Path( data["tests_path"] )

    class Pile:
        def save(env, pile_data):
            with open( env.attr.piles.path / f"{env.attr.pile.id}.json", "wb") as f:
                f.write( gzip.compress( json.dumps( pile_data ).encode('ascii') ) )

        def load(env):
            with open( env.attr.piles.path / f"{env.attr.pile.id}.json", "rb") as f:
                env.attr.pile.data = json.loads( gzip.decompress( f.read() ).decode('ascii') )    

        def random(env):
            filename = random.choice( os.listdir( env.attr.piles.path ) )
            pile_id = re.match("(.*).json", filename)[1]
            return pile_id

        def random_test(env):
            return random.choice( env.attr.pile.json["tests"] )