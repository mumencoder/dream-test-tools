
from common import *

class App(object):
    host = 'localhost'
    port = 8010
    queue_size = 256
    upload_level = 3

    def __init__(self):
        self.state = "start"
        self.sifter = DMTR.Sifter( self.queue_size )

    def generate_ast(self):
        benv = Shared.Environment()
        benv.attr.expr.depth = 3
        builder = DreamCollider.FullRandomBuilder( )
        builder.generate( benv )

        renv = Shared.Environment()
        renv.attr.test.ast = builder.toplevel
        fuzzer = DreamCollider.Fuzzer()
        renv.attr.test.ast_tokens = list(fuzzer.fuzz_shape( builder.toplevel.shape() ) )
        renv.attr.test.ngram_info = DreamCollider.NGram.compute_info( renv.attr.test.ast_tokens )

        return renv

    def state_change(self, state):
        if self.state != state:
            print( f"{self.state} -> {state}")
            self.state = state

    def upload(self, pile):
        print("uploading data...")
        content = {"tests":[], "pile": {}}
        for tenv in pile.iter_tests():
            test = {}
            test["ast"] = DreamCollider.AST.marshall( tenv.attr.test.ast )
            test["tokens"] = DreamCollider.Shape.marshall( tenv.attr.test.ast_tokens )
            test["ngrams"] = tenv.attr.test.ngram_info
            content["tests"].append( test )
        content["pile"]["level"] = pile.level
        content["pile"]["ngram_counts"] = pile.ngram_counts
        try:
            requests.post(f'http://{self.host}:{self.port}/ast_gen', data = gzip.compress( json.dumps(content).encode('ascii') ) )
            self.sifter.remove_pile( pile )
            self.state_change("start")
        except Exception as e:
            print(e)
            self.state_change("waiting")

    def run(self):
        update_time = time.time() - 8
        last_upload = time.time()
        wait_until = None

        while not self.state == "finished":
            if self.state == "start":
                merge_level = self.sifter.find_smallest_merge_level()
                if merge_level is not None:
                    piles = self.sifter.choose_random_piles( merge_level )
                    self.sifter.merge_piles( *piles )
                    self.sifter.show_index()
                elif self.sifter.has_pile_at_level(self.upload_level):
                    self.state_change( "upload" )
                else:
                    pile = DMTR.Pile.Memory()
                    self.state_change( "generate" )
            elif self.state == "generate":
                pile.add_test( self.generate_ast() )
                if pile.test_count() >= self.queue_size:
                    self.state_change("pile_up")
            elif self.state == "pile_up":
                self.sifter.add_pile( pile )
                pile = None
                self.state_change( "start" )
            elif self.state == "upload":
                print(f"upload in {time.time() - last_upload}sec")
                upload_pile = self.sifter.choose_random_pile(self.upload_level)
                self.upload(upload_pile)
                last_upload = time.time()
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
                update_time = time.time()

app = App()
app.run()