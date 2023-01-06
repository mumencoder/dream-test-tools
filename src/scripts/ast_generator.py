
from common import *

class App(object):
    host = 'localhost'
    port = 8010
    queue_size = 256

    def __init__(self):
        self.state = "generate"
        self.ast_cache = {}
        self.fresh_ast = set()

    def generate_ast(self):
        benv = Shared.Environment()
        benv.attr.expr.depth = 3
        builder = DreamCollider.FullRandomBuilder( )
        builder.generate( benv )

        upar = DreamCollider.Unparser()
        renv = Shared.Environment()
        renv.attr.ast = DreamCollider.AST.marshall( builder.toplevel )
        renv.attr.ast_tokens = upar.fuzz_shape( builder.toplevel.shape() )
        renv.attr.status = "fresh"
        return renv

    def state_change(self, state):
        if self.state != state:
            print( f"{self.state} -> {state}")
            self.state = state

    def run(self):
        running = True
        update_time = time.time() - 8
        wait_until = None
        last_directive = None

        while running:
            if len(self.fresh_ast) < self.queue_size:
                self.state_change("generate")
            elif len(self.fresh_ast) >= self.queue_size:
                if self.state == "generate":
                    self.state_change("upload")

            if self.state == "generate":
                self.fresh_ast.add( self.generate_ast( ) )
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
                    self.state_change("generate")
            else:
                raise Exception("unknown state")

            if time.time() - update_time > 10.0:
                print( f"state: {self.state}, cache: {len(self.fresh_ast)}")
                update_time = time.time()

app = App()
app.run()