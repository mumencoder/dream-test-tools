
import asyncio, time, os, sys
import shutil
import Byond, OpenDream, ClopenDream, Shared

from DTT import App
import test_runner

import random

token_types = [
    "ident", "string", "number", 
    "/", "=", 
    "#", "##",
    "(", ")", "{", "}",
    ",", ";",
    "tab", "space", "newline"
]

idents = ["define", "var", "proc", "a", "b", "c"]

def generate_test():
    tokens = []
    n_token = random.randint(2, 4)
    for i in range(0, n_token):
        tokens.append( random.choice(token_types) )
    return test_str(tokens)
        
def test_str(tokens):
    s = ""
    for token in tokens:
        if token == "ident":
            s += random.choice(idents)
        elif token == "string":
            s += '"s"'
        elif token == "number":
            s += str(123)
        elif token == "tab":
            s += '\t'
        elif token == "space":
            s += ' '
        elif token == "newline":
            s += '\n'
        else:
            s += token
    return s

class Main(App):
    async def run(self):
        env = self.env.branch()

        Byond.Install.load(env, 'default')

        while True:
            try:
                tenv = env.branch()
                tenv.attr.test.id = Shared.Random.generate_string(12)
                tenv.attr.test.root_dir = tenv.attr.dirs.ramdisc / 'tests' / tenv.attr.test.id
                tenv.attr.test.base_dir = tenv.attr.test.root_dir / f'{tenv.attr.install.platform}.{tenv.attr.tests.runner.id}'
                tenv.attr.test.text = generate_test()

                test_runner.generate_test(tenv)

                Shared.Workflow.open(env, f"test")
                Shared.Workflow.set_task(env, test_runner.byond.do_test(tenv) )
                await Shared.Workflow.run_all(self.env)
                test_runner.Report.load_result(tenv)
                if tenv.attr.result.ccode == 0:
                    print(tenv.attr.test.text, tenv.attr.result.ccode)
                time.sleep(0.01)
            finally:
                if tenv.attr.result.ccode == 255:
                    shutil.rmtree( tenv.attr.test.root_dir )

main = Main()
asyncio.run( main.start() )