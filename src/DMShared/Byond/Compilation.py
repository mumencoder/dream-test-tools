
from ..common import *

class Compilation(object):
    @staticmethod
    def create_dreammaker_command(penv):
        if not penv.attr_exists('.compilation.args'):
            args = []
        else:
            args = penv.attr.compilation.args
        preargs = ""
        postargs = ""
        for arg in args:
            if arg == "code_tree":
                preargs += "-code_tree "
            if arg == "obj_tree":
                preargs += "-o "
        if penv.attr_exists('.compilation.dm_file_path'):
            file_path = penv.attr.compilation.dm_file_path
        else:
            file_path = ''
        return f"{penv.attr.install.dir}/byond/bin/DreamMaker {preargs} {file_path} {postargs}"

    @staticmethod
    async def invoke_compiler(env):
        proc_env = os.environ
        proc_env.update( {'LD_LIBRARY_PATH':f"{env.attr.install.dir}/byond/bin"} )
        env.attr.shell.env = proc_env
        await Shared.Process.shell(env)

    async def managed_compile(env):
        menv = env.branch()
        Shared.Process.pipe_stdout(menv)
        menv.attr.shell.command = Compilation.create_dreammaker_command( menv )
        await Compilation.invoke_compiler(menv)
        env.attr.compile.stdout = menv.attr.process.stdout
        env.attr.compile.returncode = menv.attr.process.instance.returncode

    async def managed_codetree(env):
        menv = env.branch()
        Shared.Process.pipe_stdout(menv)
        menv.attr.compilation.args = ["code_tree"]
        menv.attr.shell.command = Compilation.create_dreammaker_command( menv )
        await Compilation.invoke_compiler(menv)
        env.attr.codetree.stdout = menv.attr.process.stdout
        env.attr.codetree.returncode = menv.attr.process.instance.returncode

    async def managed_objtree(env):
        menv = env.branch()
        Shared.Process.pipe_stdout(menv)
        menv.attr.compilation.args = ["obj_tree"]
        menv.attr.shell.command = Compilation.create_dreammaker_command( menv )
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

        unterminated_texts = []

        state = "header"
        while line := next_line():
            if line.startswith("DM compiler version") and state == "header":
                continue
            elif line.startswith("loading") and state == "header":
                state = "errors"
                continue
            elif line.startswith("saving ") and state == "errors":
                state = "footer"
            elif "error" in line and "warning" in line and state == "errors" or state == "footer":
                state = "footer"
            elif "Total time" in line and state == "footer":
                state = "end"
            elif line in ["error: invalid variable", 'Segmentation fault', 'free(): invalid pointer', 'Aborted', 'error: compiler passed out (please report this bug)']:
                # TODO: do something with these
                pass
            elif line.startswith("Suppressing further errors after 100"):
                pass
            elif state == "errors":
                err = Compilation.parse_error(line)
                if err is None:
                    print("===")
                    print(lines)
                    print("----")
                    print(line)
                    raise Exception("parse error")
                if err["category"] == "UNTERMINATED_TEXT":
                    unterminated_texts.append( err["lineno"] )
                if err["category"] == "UNKNOWN":
                    if err["lineno"] in unterminated_texts:
                        continue
                else:
                    result["errors"].append(err)
            else:
                raise Exception("cannot parse line --- ", state, line)
        env.attr.compile.stdout_parsed = result

    def parse_error(line):
        ss = line.split(':')
        try:
            result = {"file":ss[0], "lineno":int(ss[1]), "type":ss[2], "msg":":".join(ss[3:]), "text":line}   
            if result["type"] not in ["error", "warning"]:
                result["msg"] = ":".join(ss[2:])
        except:
            return None
        result["category"] = Compilation.error_category(result["msg"])     
        return result
    
    @staticmethod
    def all_error_categories():
        return [
            'UNDEF_VAR',
            'MISSING_CONDITION',
            'ILLEGAL_POWER',
            'EXPECTED_CONSTEXPR',
            'UNDEF_TYPEPATH',
            'EXPECTED_COLON',
            'EXPECTED_AS',
            'UNEXPECTED_IN',
            'MISSING_LEFT_ARG_TO',
            'MISSING_LEFT_ARG_IN',
            'MISSING_LEFT_ARG_ASSIGN',
            'PROC_RESERVED_WORD',
            'VAR_RESERVED_WORD',
            'MISSING_WHILE',
            'PREVIOUS_DEF',
            'DUPLICATE_DEF',
            'ZERO_DIVIDE',
            "EXPECTED_STMT_END",
            "BAD_DEFINE"
            "SLASH_MISSING_SOMETHING"
            "VAR_MISSING_SOMETHING"
            "BAD_INDENT_OR_MISSING"
            "BAD_INDENT"
            "TRY_NO_CATCH"
            "COMMA_EXPECTED_CURLY"
            "NOT_PROTOTYPE"
        ]

    @staticmethod
    def error_category(msg):
        if 'unknown directive' in msg:
            return "UNKNOWN_DIRECTIVE"
        if 'constant initializer required' in msg:
            return "CONST_INIT_REQUIRED"
        if 'invalid view dimensions' in msg:
            return "INVALID_VIEW_DIM"
        if 'may not be set at compile-time' in msg:
            return "VAR_NO_SET_COMPILETIME"
        if 'value changed' in msg:
            return "VALUE_CHANGED"
        if 'use of' in msg and 'precedes its definition' in msg:
            return "USE_PRECEDES_DEF"
        if 'procedure override precedes definition' in msg:
            return "PROC_OVERRIDE_PRECEDES_DEF"
        if 'bad or misplaced statement' in msg:
            return "BAD_OR_MISPLACED_STMT"
        if 'invalid parent type' in msg:
            return "INVALID_PARENT_TYPE"
        if 'expected "if" or "else"' in msg:
            return "EXPECTED_IF_OR_ELSE"
        if "expected 1 argument to 'in'" in msg:
            return "EXPECTED_IN_1ARG"
        if 'file-derived types are not supported' in msg:
            return "NO_FILE_SUBTYPE"
        if 'list-derived types are not supported' in msg:
            return "NO_LIST_SUBTYPE"
        if 'positive number expected' in msg:
            return "POSITIVE_NUM_EXPECTED"
        if 'empty switch statement' in msg:
            return "EMPTY_SWITCH_STMT"
        if 'empty argument not allowed' in msg:
            return "EMPTY_ARGUMENT"
        if 'unexpected symbol' in msg:
            return "UNEXPECTED_SYMBOL"
        if 'extra args' in msg:
            return "EXTRA_ARGS"
        if 'bad link' in msg:
            return "BAD_LINK"
        if 'bad embedded expression' in msg:
            return "BAD_EMBEDDED_EXPR" 
        if 'compile failed (possible infinite cross-reference loop)' in msg:
            return "POSSIBLE_INF_REF_LOOP"
        if 'Bad input type' in msg:
            return "BAD_INPUT_TYPE"
        if 'list started here' in msg:
            return 'LIST_START_HERE'
        if 'variable defined but not used' in msg:
            return "VAR_DEFN_NOT_USED"
        if 'empty type name' in msg:
            return 'EMPTY_TYPE_NAME'
        if "empty 'else' clause" in msg:
            return "EMPTY_ELSE_CLAUSE"
        if 'unused label' in msg:
            return 'UNUSED_LABEL'
        if 'label must be associated with a loop' in msg:
            return 'LABEL_NOLOOP'
        if 'it is recommended that you use an object filter or' in msg:
            return 'RECOMMEND_OBJECT_FILTER'
        if 'statement has no effect' in msg:
            return 'STATEMENT_NO_EFFECT'
        if 'operation has no effect here' in msg:
            return "OP_NO_EFFECT"
        if 'assignment in condition' in msg:
            return 'ASSIGN_IN_COND'
        if 'location of top-most unmatched {' in msg:
            return "LOC_UNMATCHED_LCURLY"
        if 'unbalanced }' in msg:
            return "UNBALANCED_RCURLY"
        if 'unbalanced )' in msg:
            return "UNBALANCED_RPAREN"
        if 'missing expression' in msg:
            return "MISSING_EXPRESSION"
        if 'expected expression' in msg:
            return "EXPECTED_EXPRESSION"
        if 'expected }' in msg:
            return "EXPECTED_RCURLY"
        if 'expected )' in msg:
            return "EXPECTED_RPAREN"
        if 'expected ]' in msg:
            return "EXPECTED_RBRACKET"
        if 'expected assignment' in msg:
            return "EXPECTED_ASSIGNMENT"
        if 'Bad input type:' in msg:
            return "BAD_INPUT_TYPE"
        if 'assignment of procedural properties takes place at compile-time' in msg:
            return "PROC_PROP_COMPILE_TIME"
        if 'No such node' in msg:
            return "NODE_NONEXIST"
        if 'bad argument definition' in msg:
            return "BAD_ARGUMENT_DEFN"
        if 'bad assignment' in msg:
            return "BAD_ASSIGN"
        if 'missing comma \',\' or right-paren' in msg:
            return "MISSING_COMMA_OR_RPAREN"
        if 'undefined var' in msg:
            return "UNDEF_VAR"
        if 'undefined proc' in msg:
            return "UNDEF_PROC"
        if 'undefined type path' in msg:
            return "UNDEF_TYPEPATH"
        if 'undefined argument type' in msg:
            return "UNDEF_ARG_TYPE"
        if 'undefined type' in msg:
            return "UNDEF_TYPE"
        if 'implicit type may only be used in an assignment' in msg:
            return "MISUSE_IMPLICIT_TYPE"
        if 'missing condition' in msg:
            return "MISSING_CONDITION"
        if 'illegal' in msg and '**' in msg:
            return "ILLEGAL_POWER"
        if 'illegal parent type' in msg:
            return "ILLEGAL_PARENT_TYPE"
        if 'expected a constant expression' in msg:
            return "EXPECTED_CONSTEXPR"
        if 'cannot change constant value' in msg:
            return "CANNOT_CHANGE_CONST"
        if "expected ':'" in msg:
            return "EXPECTED_COLON"
        if "expected as(...)" in msg:
            return "EXPECTED_AS"
        if "unexpected 'in' expression" in msg:
            return "UNEXPECTED_IN"
        if "missing left-hand argument to" in msg:
            return "MISSING_LEFT_ARG"
        if "invalid proc name: reserved word" in msg:
            return "PROC_RESERVED_WORD"
        if "invalid variable name: reserved word" in msg:
            return "VAR_RESERVED_WORD"
        if "invalid variable" in msg:
            return "INVALID_VARIABLE"
        if "invalid proc definition" in msg:
            return "INVALID_PROC_DEF"
        if "end of file reached inside of comment" in msg:
            return "EOF_INSIDE_COMMENT"
        if "beginning of comment" in msg:
            return "BEGIN_COMMENT"
        if "variable declaration not allowed here" in msg:
            return "VAR_DECL_NOT_ALLOWED"
        if "instruction not allowed here" in msg:
            return "INSTRUCTION_NOT_ALLOWED"
        if "operator not allowed here" in msg:
            return "OPERATOR_NOT_ALLOWED"
        if "statement not allowed here" in msg:
            return "STMT_NOT_ALLOWED"
        if "bad instruction" in msg:
            return "BAD_INSTRUCTION"
        if "bad variable" in msg:
            return "BAD_VAR"
        if "bad area" in msg:
            return "BAD_AREA"
        if "bad text" in msg:
            return "BAD_TEXT"
        if "bad catch" in msg:
            return "BAD_CATCH"
        if "bad number" in msg:
            return "BAD_NUMBER"
        if "bad proc" in msg:
            return "BAD_PROC"
        if "bad file" in msg:
            return "BAD_FILE"
        if "bad cursor" in msg:
            return "BAD_CURSOR"
        if "bad mob" in msg:
            return "BAD_MOB"
        if "bad constant" in msg:
            return "BAD_CONSTANT"
        if "bad size" in msg:
            return "BAD_SIZE"
        if "bad turf" in msg:
            return "BAD_TURF"
        if "bad if block" in msg:
            return "BAD_IF_BLOCK"
        if "bad for block" in msg:
            return "BAD_FOR_BLOCK"
        if "error at 'end of file': variable not defined" in msg:
            return "EOF_ERROR_VAR_NOT_DEFINED"
        if "invalid script" in msg:
            return "INVALID_SCRIPT"
        if "expected TOPDOWN_MAP" in msg:
            return "EXPECTED_MAP_FLAG"
        if "not an integer" in msg:
            return "NOT_INTEGER"
        if "cannot assign a proc!" in msg:
            return "PROC_NOASSIGN"
        if "expected proc definition" in msg:
            return "EXPECTED_PROC_DEFN"
        if "expected var or proc name after . operator" in msg:
            return "EXPECTED_VAR_OR_PROC_AFTER_DOT_OPERATOR"
        if "expected src on left-hand side" in msg:
            return "EXPECTED_SRC_ON_LHS"
        if "expected var or proc name after .? operator" in msg:
            return "EXPECTED_VAR_OR_PROC_AFTER_DOTQUESTION_OPERATOR"
        if "expected var or proc name after ?. operator" in msg:
            return "EXPECTED_VAR_OR_PROC_AFTER_QUESTIONDOT_OPERATOR"
        if "This appears like the old syntax for new()" in msg:
            return "OLD_NEW_SYNTAX"
        if "re-initialization of global var" in msg:
            return "GLOBAL_REINIT"
        if "use call() to call a proc by reference" in msg:
            return "USE_CALL_PROC_REF"
        if "out of bounds" in msg:
            return "OUT_OF_BOUNDS"
        if "expected 1 or 0" in msg:
            return "EXPECTED_VALUE"
        if "expected 0, 1, or 2" in msg:
            return "EXPECTED_VALUE"
        if "expected matrix or null" in msg:
            return "EXPECTED_VALUE"
        if "expected filter, list, or null" in msg:
            return "EXPECTED_VALUE"
        if "expected object or null" in msg:
            return "EXPECTED_VALUE"
        if "expected color, list, or null" in msg:
            return "EXPECTED_VALUE"
        if "expected 0-7" in msg:
            return "EXPECTED_VALUE"
        if "Expected null, num, or text" in msg:
            return "EXPECTED_VALUE"
        if "expected list" in msg:
            return "EXPECTED_LIST"
        if "expected newlist" in msg:
            return "EXPECTED_NEWLIST"
        if "implicit source" in msg:
            return "IMPLICIT_SOURCE"
        if "expected 0-3" in msg:
            return "EXPECTED_VALUE"
        if "input type" in msg and "must be atomic" in msg:
            return "INPUT_TYPE_NOT_ATOMIC"
        if "arglist() or named arguments cannot be used" in msg:
            return "CANNOT_USE_ARGLIST"
        if "list doubly initialized" in msg:
            return "LIST_DOUBLE_INIT"
        if "proc definition not allowed inside another proc" in msg:
            return "PROC_IN_PROC"
        if "definition is here" in msg:
            return "DEFN_HERE"
        if "unknown variable type" in msg:
            return "UNKNOWN_VARIABLE_TYPE"
        if "too many vars in project" in msg:
            return "TOO_MANY_VARS"
        if "invalid expression" in msg:
            return "INVALID_EXPRESSION"
        if "invalid gender" in msg:
            return "INVALID_GENDER"
        if "missing while statement" in msg:
            return "MISSING_WHILE"
        if "missing =" in msg:
            return "MISSING_EQUALS"
        if "continue failed" in msg:
            return "CONTINUE_FAILED"
        if "break failed" in msg:
            return "BREAK_FAILED"
        if "value not allowed here" in msg:
            return "VALUE_NOT_ALLOWED"
        if "expected range is" in msg:
            return "EXPECTED_RANGE"
        if "previous definition" in msg:
            return "PREVIOUS_DEF"
        if "duplicate definition" in msg:
            return "DUPLICATE_DEF"
        if "attempted division by zero" in msg:
            return "ZERO_DIVIDE"
        if "expected end of statement" in msg:
            return "EXPECTED_STMT_END"
        if "definition out of place" in msg:
            return "BAD_DEFINE"
        if "inconsistent indentation or missing" in msg:
            return "BAD_INDENT_OR_MISSING"
        if "inconsistent indentation" in msg:
            return "BAD_INDENT"
        if "'else' clause without preceding 'if' statement" in msg:
            return "ELSE_WITHOUT_IF"
        if "unterminated text" in msg:
            return "UNTERMINATED_TEXT"
        if "try without catch" in msg:
            return "TRY_NO_CATCH"
        if "catch without try" in msg:
            return "CATCH_NO_TRY"
        if "not a prototype" in msg:
            return "NOT_PROTOTYPE"
        if "icon width or height cannot exceed 256" in msg:
            return "ICON_BAD_DIM"
        return 'UNKNOWN'