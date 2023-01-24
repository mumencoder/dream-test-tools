
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
        env.attr.compilation.returncode = penv.attr.process.instance.returncode

    async def managed_compile(env):
        env = env.branch()
        env.attr.process.stdout = open(env.attr.compilation.root_dir / 'byond.compile.stdout.txt', "w")
        try:
            await Compilation.invoke_compiler(env)
        finally:
            env.attr.process.stdout.close()

        with open(env.attr.compilation.root_dir / 'byond.compile.returncode.txt', "w") as f:
            f.write( str(env.attr.compilation.returncode) )

        return env

    def load_compile(env):
        with open( env.attr.compilation.root_dir / 'byond.compile.stdout.txt', "r" ) as f:
            env.attr.compilation.stdout = f.read()
        with open( env.attr.compilation.root_dir / 'byond.compile.returncode.txt', "r" ) as f:
            env.attr.compilation.returncode = int(f.read())

    async def managed_codetree(env):
        env = env.branch()
        env.attr.compilation.args = ["code_tree"]
        env.attr.process.stdout = open(env.attr.compilation.root_dir / 'byond.codetree.stdout.txt', "w")
        try:
            await Compilation.invoke_compiler(env)
        finally:
            env.attr.process.stdout.close()

        return env

    async def managed_objtree(env):
        env = env.branch()
        env.attr.compilation.args = ["obj_tree"]
        env.attr.process.stdout = open(env.attr.compilation.root_dir / 'byond.objtree.stdout.txt', "w")
        try:
            await Compilation.invoke_compiler(env)
        finally:
            env.attr.process.stdout.close()

        return env

    def load_objtree(env):
        with open( env.attr.compilation.root_dir / 'byond.objtree.stdout.txt', "r" ) as f:
            env.attr.compilation.objtree_text = f.read()
        
        lines = []
        for line in env.attr.compilation.objtree_text.split('\n'):
            if line.startswith("loading"):
                continue
            lines.append( line )
        xml = "\n".join( lines )

        objtree_xml = minidom.parseString( xml )
        env.attr.compilation.objtree_xml = objtree_xml

        def readDM(node):
            if node.nodeType == node.ELEMENT_NODE and node.nodeName == "dm":
                return True
            else:
                return None

        def readObject(node):
            if node.nodeType == node.ELEMENT_NODE and node.nodeName == "object":
                obj_name = None
                subobjs = []
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
                    raise Exception(leafnode)
                return {"name":obj_name, "subobjs":subobjs}
            else:
                return None

        def readProc(node):
            if node.nodeType == node.ELEMENT_NODE and node.nodeName == "proc":
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
        env.attr.compilation.objtree = rootobjs