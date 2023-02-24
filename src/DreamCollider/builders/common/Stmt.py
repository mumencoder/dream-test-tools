
from ...common import *

from ...Tree import *
from . import Var


class RandomStmt(object):
    def config_stmt(self, config):
        config.set_choice("stmt.type", 
            expr=1, 
            output_normal=10, output_here=1, output_irregular=1,
            var_define=10, 
            _return=2, _break=4, _continue=4, goto=4, label=4,
            _del=10, 
            set=2, 
            spawn=10, 
            _if=10, switch=10,
            _for=10, forenum=10, _while=10, dowhile=10,
            _try=10, throw=10,
        )

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
            body.append( self.create_proc_stmt( env ) )
        return body

    def create_proc_stmt(self, env):
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
                stmt = AST.Stmt.Expression.new( expr=self.create_var_expr(env) )
            case "output_normal":
                stmt = AST.Stmt.Expression.new(
                    expr=AST.Op.ShiftLeft.new(
                        exprs=[
                            AST.Expr.Identifier.new(name = "world"), self.create_var_expr(env),
                            self.create_var_expr(env)
                        ]
                    )
                )
            case "output_here":
                stmt = self.print_here_stmt(env)
            case "output_irregular":
                stmt = AST.Stmt.Expression.new(
                    expr=AST.Op.ShiftLeft.new(
                        exprs=[
                            self.create_var_expr(env),
                            self.create_var_expr(env)
                        ]
                    )
                )
            case "var_define":
                stmt = AST.Stmt.VarDefine.new( 
                    name=Var.RandomVarName(env, self),
                    var_type=Var.RandomVarMod(env, self),
                    expr=self.create_var_expr(env)
                )
            #TODO: no expression after return
            case "_return":
                stmt = AST.Stmt.Return.new(
                    expr=self.create_var_expr(env)
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
                    expr=self.create_var_expr(env)
                )
            case "set":
                stmt = AST.Stmt.Set.new(
                    attr=random.choice(["attr1", "attr2", "attr3"]),
                    expr=self.create_var_expr(env)
                )
            case "spawn":
                stmt = AST.Stmt.Spawn.new(
                    delay=self.create_var_expr(env),
                    body=self.RandomBody(env)
                )
            case "_if":
                stmt = AST.Stmt.If.new(
                    condition=self.create_var_expr(env),
                    truebody=self.RandomBody(env),
                    falsebody=self.RandomBody(env)
                )
            case "switch":
                nifcases = random.choice([0,1,1,1,1,2,2,2,3,3,4])
                welse = random.choice([5,5,5,5,5,4,4,4,4,3,3,3,2,2,1])
                cases = []
                for i in range(0,6):
                    if i < nifcases:
                        cases.append( AST.Stmt.Switch.IfCase.new(condition=self.create_var_expr(env), body=self.RandomBody(env)) )
                    if i == welse:
                        cases.append( AST.Stmt.Switch.ElseCase.new(body=self.RandomBody(env)) )
                stmt = AST.Stmt.Switch.new(
                    switch_expr=self.create_var_expr(env),
                    cases=cases
                )
            case "_for":
                stmt = AST.Stmt.For.new(
                    expr1=self.create_var_expr(env),
                    expr2=self.create_var_expr(env),
                    expr3=self.create_var_expr(env),
                    body=self.RandomBody(env)
                )
            case "forenum":
                stmt = AST.Stmt.ForEnumerator.new(
                    var_expr=self.create_var_expr(env),
                    list_expr=self.create_var_expr(env),
                    body=self.RandomBody(env)
                )
            case "_while":
                stmt = AST.Stmt.While.new(
                    condition=self.create_var_expr(env),
                    body=self.RandomBody(env)
                )
            case "dowhile":
                stmt = AST.Stmt.DoWhile.new(
                    condition=self.create_var_expr(env),
                    body=self.RandomBody(env)
                )
            case "_try":
                stmt = AST.Stmt.Try.new(
                    try_body=self.RandomBody(env),
                    catch_param=AST.Stmt.Try.Catch.new( expr= self.create_var_expr(env) ),
                    catch_body=self.RandomBody(env)
                )
            case "throw":
                stmt = AST.Stmt.Throw.new(
                    expr=self.create_var_expr(env)
                )
            case _:
                raise Exception("unknown stmt option", stmt_type)

        return stmt