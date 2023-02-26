
from .. import Byond

if import_dotnet:
    from .Dotnet import clr
    import ClopenDream
    import DMCompiler
    from DMCompiler.Compiler.DM import DMAST
    from System import *
    import System.Threading.Tasks
    import System.IO
    from System.Collections.Generic import List

class Compilation:
    async def prepare_empty(ienv, oenv):
        with open( ienv.attr.test.root_dir / 'empty.dm', "w") as f:
            f.write('')

        ienv.attr.compilation.dm_file_path = ienv.attr.test.root_dir / 'empty.dm'
        ienv.attr.compilation.args = ["code_tree"]
        await Byond.managed_codetree(ienv)

        with open( ienv.attr.test.root_dir / 'byond.compile.stdout.txt', "r") as f:
            codetree = f.read()
        oenv.attr.empty.codetree = codetree

        p = ClopenDream.Parser()
        try:
            empty_root = p.BeginParse( System.IO.StringReader( oenv.attr.empty.codetree ) )
            empty_root.FixLabels()
        except Exception as e:
            print(e)
            for error in p.errors:
                print(error)
        oenv.attr.empty.root = empty_root

        l = List[System.String]()
        l.Add( str(ienv.attr.compilation.dm_file_path) )
        state = DMCompiler.DMCompiler.GetAST( l )

        oenv.attr.empty.open_compile = state

    async def clopen_ast(tenv):
        env = tenv.branch()
        codetree = System.IO.StringReader( env.attr.test.files.byond_codetree_stdout )

        result = ClopenDream.ClopenDream.PrepareAST( codetree, tenv.attr.empty.root )

        if "parser_exc" in result:
            tenv.attr.test.metadata.paths.clparser_throw = 'clparser_throw.txt'
            with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clparser_throw, "w") as f:
                f.write( result["parser_exc"].StackTrace + '\n')
                f.write( "===\n" )
        else:
            if tenv.attr_exists( '.test.metadata.paths.clparser_throw' ):
                del tenv.attr.test.metadata.paths.clparser_throw

        if len(result["parser"].errors) > 0:
            tenv.attr.test.metadata.paths.clparser_errors = 'clparser_errors.txt'
            with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clparser_errors, "w") as f:
                for error in result["parser"].errors:
                    f.write( error + '\n' )
                    f.write( "===\n" )
        else:
            if tenv.attr_exists( '.test.metadata.paths.clparser_errors' ):
                del tenv.attr.test.metadata.paths.clparser_errors

        if len(result["parser"].byond_errors) > 0:
            tenv.attr.test.metadata.paths.byond_errors = 'byond_errors.txt'
            with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.byond_errors, "w") as f:
                for error in result["parser"].byond_errors:
                    f.write( error.Text + '\n' )
        else:
            if tenv.attr_exists( '.test.metadata.paths.byond_errors' ):
                del tenv.attr.test.metadata.paths.byond_errors

        if "root_node" in result and result["root_node"] is not None:
            tenv.attr.test.metadata.paths.clparser_tree = 'clparser_tree.txt'
            with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clparser_tree, "w") as f:
                f.write( result["root_node"].PrintLeaves(128) )
        else:
            if tenv.attr_exists( '.test.metadata.paths.clparser_tree' ):
                del tenv.attr.test.metadata.paths.clparser_tree

        if "convert_exc" in result:
            tenv.attr.test.metadata.paths.clconvert_throw = 'clconvert_throw.txt'
            with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clconvert_throw, "w") as f:
                f.write( result["convert_exc"].Source + '\n')
                f.write( result["convert_exc"].Message + '\n')
                f.write( result["convert_exc"].StackTrace + '\n')
                f.write( "===\n" )
        else:
            if tenv.attr_exists( '.test.metadata.paths.clconvert_throw' ):
                del tenv.attr.test.metadata.paths.clconvert_throw

        if len(result["converter"].errors) > 0:
            tenv.attr.test.metadata.paths.clconvert_errors = 'clconvert_errors.txt'
            with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clconvert_errors, "w") as f:
                for error in result["converter"].errors:
                    f.write( error + '\n' )
                    f.write( "===\n" )
        else:
            if tenv.attr_exists( '.test.metadata.paths.clconvert_errors' ):
                del tenv.attr.test.metadata.paths.clconvert_errors

        Metadata.save_test(tenv)

    def collider_errors_info( model ):
        info = {"lines":[]}
        for lineno, errid in model["errors"]:
            info["lines"].append( {"lineno":lineno, "text":f"{lineno}:{errid}"} )
        info["width"] = 20
        return info

    # TODO: this may not work for macro expansion
    def clparse_tree(text):
        for line in text.split('\n'):
            ss = line.split("|||")
            if len(ss) != 3:
                continue
            ff = ss[2].split(":")
            if len(ff) >= 2:
                yield {"file":ff[0].strip(), "lineno":int(ff[1]), "text":line }
                
    def clparser_tree_info( text ):
        info = {"lines": sorted(list(Display.clparse_tree(text)), key=lambda line: line["lineno"]) }
        info["lines"] = [ line for line in info["lines"] if line["file"] == 'test.dm' and line["lineno"] != 0 ]
        info["width"] = max( [len(line["text"]) for line in info["lines"] ]) + 8
        for i in range(0, len(info["lines"])-1):
            if info["lines"][i+1]["lineno"] == 0:
                info["lines"][i+1]["lineno"] = info["lines"][i]["lineno"]
        return info
        
    async def run_meta(tenv):
        lexer = ClopenDream.DMLexer()
        get_file(tenv, 'dm_file')
        src = ClopenDream.SourceText( tenv.attr.test.files.dm_file )
        lexer.Include( src )

        parsing = True
        while parsing:
            token = lexer.NextToken()
            if token.K == ClopenDream.DMToken.Kind.EndOfFile:
                parsing = False
            print( token.ToString() )