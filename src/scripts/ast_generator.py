
from common import *

class App(object):
    host = 'localhost'
    port = 8010
    queue_size = 256

    def __init__(self):
        self.state = "start"
        self.fresh_ast = set()

        self.sifter = DMTR.Sifter( self.queue_size )

    def generate_ast(self):
        benv = Shared.Environment()
        benv.attr.expr.depth = 3
        builder = DreamCollider.FullRandomBuilder( )
        builder.generate( benv )

        upar = DreamCollider.Unparser()
        renv = Shared.Environment()
        renv.attr.ast = DreamCollider.AST.marshall( builder.toplevel )
        renv.attr.ast_tokens = upar.fuzz_shape( builder.toplevel.shape() )
        renv.attr.ngram_info = DreamCollider.NGram.compute_info( renv.attr.ast_tokens )
        renv.attr.status = "fresh"
        return renv

    def state_change(self, state):
        if self.state != state:
            print( f"{self.state} -> {state}")
            self.state = state

    def run(self):
        update_time = time.time() - 8
        wait_until = None

        while not self.state == "finished":
            if self.state == "start":
                pile = DMTR.Pile.Memory()
                self.state_change( "generate" )
            elif self.state == "generate":
                pile.add_test( self.generate_ast() )
                if pile.test_count() >= self.queue_size:
                    self.state_change("pile_up")
            elif self.state == "pile_up":
                self.sifter.add_pile( pile )
                self.state_change( "sift" )
            elif self.state == "sift":
                merge_level = self.sifter.find_smallest_merge_level()
                if merge_level is not None:
                    piles = self.sifter.choose_random_piles( merge_level )
                    result = self.sifter.merge_piles( *piles )
                self.state_change( "start" )
            elif self.state == "upload":
                print("uploading data...")
                content = []    
                for renv in self.fresh_ast:
                    if renv.attr.status != "fresh":
                        continue
                    content.append( renv.attr.ast )
                    renv.attr.uploaded = True
                if len(content) != 0:
                    try:
                        requests.post(f'http://{self.host}:{self.port}/ast_gen', data = gzip.compress( json.dumps(content).encode('ascii') ) )
                        for renv in self.fresh_ast:
                            renv.attr.status = "uploaded"
                    except Exception as e:
                        print(e)
                        self.state_change("waiting")
                else:
                    self.state_change("waiting")
            elif self.state == "waiting":
                if wait_until is None:
                    wait_until = time.time() + 10
                time.sleep(0.1)
                if time.time() > wait_until:
                    wait_until = None
                    self.state_change("start")
            else:
                raise Exception("unknown state")

            if time.time() - update_time > 10.0:
                print( f"state: {self.state}, cache: {len(self.fresh_ast)}")
                update_time = time.time()

app = App()
app.run()