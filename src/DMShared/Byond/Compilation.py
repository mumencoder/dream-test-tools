
from ..common import *

class Compilation(object):
    @staticmethod
    def create_dreammaker_command(penv, args=[]):
        preargs = ""
        postargs = ""
        for arg in args:
            if arg == "code_tree":
                preargs += "-code_tree "
            if arg == "obj_tree":
                preargs += "-o "
        return f"{penv.attr.install.dir}/byond/bin/DreamMaker {preargs} {penv.attr.compilation.dm_file_path} {postargs}"

    @staticmethod
    async def invoke_compiler(env):
        penv = env.branch()
        if not penv.attr_exists('.compilation.args'):
            penv.attr.compilation.args = []

        proc_env = os.environ
        proc_env.update( {'LD_LIBRARY_PATH':f"{penv.attr.install.dir}/byond/bin"} )
        penv.attr.shell.env = proc_env
        penv.attr.shell.command = Compilation.create_dreammaker_command( penv, penv.attr.compilation.args )
        await Shared.Process.shell(penv)

    async def managed_compile(env):
        menv = env.branch()
        await Compilation.invoke_compiler(menv)
        env.attr.compile.stdout = menv.attr.process.stdout
        env.attr.compile.returncode = menv.attr.process.instance.returncode

    async def managed_codetree(env):
        menv = env.branch()
        menv.attr.compilation.args = ["code_tree"]
        await Compilation.invoke_compiler(env)
        env.attr.codetree.stdout = menv.attr.process.stdout
        env.attr.codetree.returncode = menv.attr.process.instance.returncode

    async def managed_objtree(env):
        menv = env.branch()
        menv.attr.compilation.args = ["obj_tree"]
        await Compilation.invoke_compiler(menv)
        env.attr.objtree.stdout = menv.attr.process.stdout
        env.attr.objtree.returncode = menv.attr.process.instance.returncode

    def load_objtree(senv, denv):
        lines = []
        for line in denv.attr.compilation.objtree_stdout.split('\n'):
            if line.startswith("loading"):
                continue
            if ':error:' in line:
                continue
            if ':warning:' in line:
                continue
            lines.append( line )
        xml = "\n".join( lines )

        try:
            objtree_xml = minidom.parseString( xml )
        except:
            denv.attr.compilation.objtree_xml = None
            return
        denv.attr.compilation.objtree_xml = objtree_xml

        def readDM(node):
            if node.nodeType == node.ELEMENT_NODE and node.nodeName == "dm":
                return True
            else:
                return None

        def readObject(node):
            if node.nodeType == node.ELEMENT_NODE and node.nodeName in ["object", "area", "turf", "obj", "mob"]:
                obj_name = None
                subobjs = []
                line = None
                if "file" in node.attributes:
                    line = int(node.attributes["file"].value.split(":")[1])
                for leafnode in node.childNodes:
                    if readWS(leafnode):
                        continue
                    if leafnode.nodeType == node.TEXT_NODE:
                        if obj_name is not None:
                            raise Exception(leafnode)
                        obj_name = leafnode.nodeValue.strip()
                        continue
                    obj = readObject(leafnode)
                    if obj is not None:
                        subobjs.append( obj )
                        continue
                    if readProc(leafnode):
                        continue
                    if readVar(leafnode):
                        continue
                    if readVal(leafnode):
                        continue
                    raise Exception(leafnode)
                return {"name":obj_name, "subobjs":subobjs, "line":line}
            else:
                return None

        def readVar(node):
            if node.nodeType == node.ELEMENT_NODE and node.nodeName in ["var"]:
                return True
            else:
                return False

        def readVal(node):
            if node.nodeType == node.ELEMENT_NODE and node.nodeName in ["val"]:
                return True
            else:
                return False

        def readProc(node):
            if node.nodeType == node.ELEMENT_NODE and node.nodeName in ["proc", "verb"]:
                return True
            else:
                return False

        def readWS(node):
            if node.nodeType == node.TEXT_NODE:
                for v in node.nodeValue:
                    if v in ["\n", "\t", " "]:
                        continue
                    return None
                return True
            return None

        for leafnode in objtree_xml.childNodes:
            rootobjs = None
            if readDM(leafnode):
                if rootobjs is not None:
                    raise Exception(leafnode)
                rootobjs = []
                for leafnode in leafnode.childNodes:
                    obj = readObject(leafnode)
                    if obj is not None:
                        rootobjs.append(obj)
                        continue
                    if readWS(leafnode):
                        continue
                    if readProc(leafnode):
                        continue
                    if readVar(leafnode):
                        continue
                    if readVal(leafnode):
                        continue
                    print(xml)
                    raise Exception(leafnode)
            if readWS(leafnode):
                continue

            raise Exception(leafnode)

        nodes_left = list(rootobjs)
        while len(nodes_left) > 0:
            node = nodes_left[-1]
            nodes_left.pop()
            if "parent" not in node:
                node["path"] = tuple([node["name"]])
            else:
                node["path"] = node["parent"]["path"] + tuple([node["name"]])

            if "subobjs" in node:
                for subobj in node["subobjs"]:
                    subobj["parent"] = node
                nodes_left += list(node["subobjs"])
        denv.attr.compilation.objtree = rootobjs

    def iter_objtree(env):
        if not env.attr_exists('.compilation.objtree'):
            return None
        nodes_left = list(env.attr.compilation.objtree)
        while len(nodes_left) > 0:
            node = nodes_left[-1]
            nodes_left.pop()
            yield node
            if "subobjs" in node:
                nodes_left += list(node["subobjs"])

    def parse_compile_stdout(env):
        lines = env.attr.compile.stdout_text.split('\n')
        line_i = 0
        def next_line():
            nonlocal line_i
            if line_i >= len(lines):
                return None
            line = lines[line_i]
            line_i += 1
            return line
        
        result = {"errors":[]}

        state = "header"
        while line := next_line():
            if line.startswith("DM compiler version") and state == "header":
                continue
            elif line.startswith("loading") and state == "header":
                state = "errors"
                continue
            elif "error" in line and "warning" in line and state == "errors":
                state = "footer"
            elif "Total time" in line and state == "footer":
                state = "end"
            elif state == "errors":
                err = Compilation.parse_error(line)
                result["errors"].append(err)
            else:
                raise Exception("cannot parse line --- ", state, line)
        env.attr.compile.stdout_parsed = result

    def parse_error(line):
        ss = line.split(':')
        result = {"file":ss[0], "lineno":int(ss[1]), "type":ss[2], "msg":":".join(ss[3:]), "text":line}   
        result["category"] = Compilation.error_category(result["msg"])     
        return result
    
    @staticmethod
    def error_category(msg):
        if 'undefined var' in msg:
            return "UNDEF_VAR"
        if 'missing condition' in msg:
            return "MISSING_CONDITION"
        if 'illegal' in msg and '**' in msg:
            return "ILLEGAL_POWER"
        if 'expected a constant expression' in msg:
            return "EXPECTED_CONSTEXPR"
        if 'undefined type path' in msg:
            return "UNDEF_TYPEPATH"
        if "expected ':'" in msg:
            return "EXPECTED_COLON"
        if "expected as(...)" in msg:
            return "EXPECTED_AS"
        if "unexpected 'in' expression" in msg:
            return "UNEXPECTED_IN"
        if "missing left-hand argument to to" in msg:
            return "MISSING_LEFT_ARG_TO"
        if "missing left-hand argument to in" in msg:
            return "MISSING_LEFT_ARG_IN"
        if "missing left-hand argument to =" in msg:
            return "MISSING_LEFT_ARG_ASSIGN"
        if "invalid proc name: reserved word" in msg:
            return "PROC_RESERVED_WORD"
        if "invalid variable name: reserved word" in msg:
            return "VAR_RESERVED_WORD"
        if "missing while statement" in msg:
            return "MISSING_WHILE"
        if "previous definition" in msg:
            return "DUPLICATE_DEF"
        if "duplicate definition" in msg:
            return "DUPLICATE_DEF"
        if "attempted division by zero" in msg:
            return "ZERO_DIVIDE"
        if "var: expected end of statement" in msg:
            return "EXPECTED_STMT_END"
        if "definition out of place" in msg:
            return "BAD_DEFINE"
        if "/: missing comma ',' or right-paren ')'" in msg:
            return "SLASH_MISSING_SOMETHING"
        if "var: missing comma ',' or right-paren ')'" in msg:
            return "VAR_MISSING_SOMETHING"
        if "inconsistent indentation or missing" in msg:
            return "BAD_INDENT_OR_MISSING"
        if "inconsistent indentation" in msg:
            return "BAD_INDENT"
        if "try without catch" in msg:
            return "TRY_NO_CATCH"
        if ",: expected }" in msg:
            return "COMMA_EXPECTED_CURLY"
        if "not a prototype" in msg:
            return "NOT_PROTOTYPE"
        return 'UNKNOWN'