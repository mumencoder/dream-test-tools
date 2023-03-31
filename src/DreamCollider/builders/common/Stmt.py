
from ...common import *

from ...Tree import *
from . import Var

from .Config import *

class RandomStmt(Configurable):
    def print_here_stmt(self, env):
        return AST.Stmt.Expression.new( 
            expr=AST.Op.ShiftLeft.new( 
                exprs=[ 
                    AST.Expr.Identifier.new(name="world"), 
                    AST.TextNode.new(text='"[.....]"')]
            )
        )
   
    def RandomLabel(self, env):
        return random.choice( ["label1", "label2", "label3"] )

    def RandomBody(self, env):
        nstmt = random.choice([0,1,1,1,1,2,2,2,3,3,4])
        body = []
        for i in range(0, nstmt):
            body.append( self( env ) )
        return body

    def __call__(self, env):
        def has_body(ty):
            if ty in [
                "expr", 
                "output_normal", "output_here", "output_irregular", 
                "var_define",
                "_return", "_break", "_continue", "goto",
                "_del",
                "set",
                "throw"]:
                return False
            else:
                return True

        stmt_type = None
        while stmt_type is None:
            stmt_type = self.config.choose_option( "stmt.type" )
            if env.attr.proc_max_depth == 0 and has_body(stmt_type):
                stmt_type = None

        env.attr.proc_max_depth = random.randint(0,max(0,env.attr.proc_max_depth-1))
        match stmt_type:
            case "expr":
                stmt = AST.Stmt.Expression.new( expr=self.generate_expression(env) )
            case "output_normal":
                stmt = AST.Stmt.Expression.new(
                    expr=AST.Op.ShiftLeft.new(
                        exprs=[
                            AST.Expr.Identifier.new(name = "world"), self.generate_expression(env),
                            self.generate_expression(env)
                        ]
                    )
                )
            case "output_here":
                stmt = self.print_here_stmt(env)
            case "output_irregular":
                stmt = AST.Stmt.Expression.new(
                    expr=AST.Op.ShiftLeft.new(
                        exprs=[
                            self.generate_expression(env),
                            self.generate_expression(env)
                        ]
                    )
                )
            case "var_define":
                stmt = AST.Stmt.VarDefine.new( 
                    name=self.generate_var_name(env),
                    var_type=self.generate_var_path(env),
                    expr=self.generate_expression(env)
                )
            #TODO: no expression after return
            case "_return":
                stmt = AST.Stmt.Return.new(
                    expr=self.generate_expression(env)
                )
            case "_break":
                stmt = AST.Stmt.Break.new(
                    label=self.RandomLabel(env)
                )
            case "_continue":
                stmt = AST.Stmt.Continue.new(
                    label=self.RandomLabel(env)
                )
            case "goto":
                stmt = AST.Stmt.Goto.new(
                    label=self.RandomLabel(env)
                )
            case "label":
                stmt = AST.Stmt.Label.new(
                    name=self.RandomLabel(env),
                    has_colon=random.choice([True, True, True, False]),
                    body=self.RandomBody(env)
                )
            case "_del":
                stmt = AST.Stmt.Del.new(
                    expr=self.generate_expression(env)
                )
            case "set":
                stmt = AST.Stmt.Set.new(
                    attr=random.choice(["attr1", "attr2", "attr3"]),
                    expr=self.generate_expression(env)
                )
            case "spawn":
                stmt = AST.Stmt.Spawn.new(
                    delay=self.generate_expression(env),
                    body=self.RandomBody(env)
                )
            case "_if":
                stmt = AST.Stmt.If.new(
                    condition=self.generate_expression(env),
                    truebody=self.RandomBody(env),
                    falsebody=self.RandomBody(env)
                )
            case "switch":
                nifcases = random.choice([0,1,1,1,1,2,2,2,3,3,4])
                welse = random.choice([5,5,5,5,5,4,4,4,4,3,3,3,2,2,1])
                cases = []
                for i in range(0,6):
                    if i < nifcases:
                        cases.append( AST.Stmt.Switch.IfCase.new(condition=self.generate_expression(env), body=self.RandomBody(env)) )
                    if i == welse:
                        cases.append( AST.Stmt.Switch.ElseCase.new(body=self.RandomBody(env)) )
                stmt = AST.Stmt.Switch.new(
                    switch_expr=self.generate_expression(env),
                    cases=cases
                )
            case "_for":
                stmt = AST.Stmt.For.new(
                    expr1=self.generate_expression(env),
                    expr2=self.generate_expression(env),
                    expr3=self.generate_expression(env),
                    body=self.RandomBody(env)
                )
            case "forenum":
                stmt = AST.Stmt.ForEnumerator.new(
                    var_expr=self.generate_expression(env),
                    list_expr=self.generate_expression(env),
                    body=self.RandomBody(env)
                )
            case "_while":
                stmt = AST.Stmt.While.new(
                    condition=self.generate_expression(env),
                    body=self.RandomBody(env)
                )
            case "dowhile":
                stmt = AST.Stmt.DoWhile.new(
                    condition=self.generate_expression(env),
                    body=self.RandomBody(env)
                )
            case "_try":
                stmt = AST.Stmt.Try.new(
                    try_body=self.RandomBody(env),
                    catch_param=AST.Stmt.Try.Catch.new( expr= self.generate_expression(env) ),
                    catch_body=self.RandomBody(env)
                )
            case "throw":
                stmt = AST.Stmt.Throw.new(
                    expr=self.generate_expression(env)
                )
            case _:
                raise Exception("unknown stmt option", stmt_type)

        return stmt