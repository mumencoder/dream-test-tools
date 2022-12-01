

from common import *

env = base_setup()
load_opendream(env.attr.envs.opendream)

import System
from System.Reflection import *
import System.IO
from System.Collections.Generic import List
import System.Threading.Tasks

import DMCompiler
import DMCompiler.Compiler.DM
import OpenDreamShared

#from Content.Tests import DMTests
#from Robust.Shared.IoC import IoCManager
#from OpenDreamRuntime import IDreamManager

def check_known_type(ty):
    if ty.Equals( OpenDreamShared.Compiler.Location ):
        return "ignore"
    elif ty.IsAssignableTo( System.String ):
        return "leaf"
    elif ty.IsAssignableTo( System.Int32 ):
        return "leaf"
    elif ty.IsAssignableTo( System.Single ):
        return "leaf"
    elif ty.IsAssignableTo( System.Boolean ):
        return "leaf"
    elif ty.IsArray and check_known_type(ty.GetElementType()):
        return "trunk"
    elif ty.IsGenericType and ty.GetGenericTypeDefinition( ).FullName == "System.Nullable`1":
        return check_known_type( ty.GetGenericArguments()[0])
    elif ty.IsAssignableTo( DMCompiler.Compiler.DM.DMASTNode ):
        return "trunk"
    elif ty.IsAssignableTo( OpenDreamShared.Dream.DreamPath ):
        return "leaf"
    elif ty.IsAssignableTo( OpenDreamShared.Dream.Procs.DMValueType ):
        return "leaf"
    elif ty.IsAssignableTo( DMCompiler.Compiler.DM.DMASTProcStatementSwitch.SwitchCase ):
        return "trunk"
    elif ty.IsAssignableTo( DMCompiler.Compiler.DM.DMASTPick.PickValue ):
        return "trunk"
    elif ty.IsAssignableTo( DMCompiler.Compiler.DM.DMASTCallable ):
        return "leaf"
    elif ty.IsAssignableTo( DMCompiler.Compiler.DM.DMASTDereference.DereferenceType ):
        return "leaf"
    else:
        return None

def load_ast_types():
    asm = Assembly.GetAssembly(DMCompiler.Compiler.DM.DMASTVisitor)

    ast_categories = collections.defaultdict(list)
    for ty in asm.GetTypes():
        if ty.IsAssignableTo( DMCompiler.Compiler.DM.DMASTNode ):
            if not ty.Name.startswith('DMAST'):
                raise Exception("Incorrectly named node")

            if ty.Equals( DMCompiler.Compiler.DM.DMASTNode ):
                pass
            elif ty.Equals( DMCompiler.Compiler.DM.DMASTStatement ):
                pass
            elif ty.Equals( DMCompiler.Compiler.DM.DMASTProcStatement ):
                pass
            elif ty.Equals( DMCompiler.Compiler.DM.DMASTExpression ):
                pass
            elif ty.Equals( DMCompiler.Compiler.DM.DMASTFile ):
                pass
            elif ty.BaseType.Equals( DMCompiler.Compiler.DM.DMASTStatement ):
                pass
                ast_categories[ ty.BaseType ].append( ty )
            elif ty.BaseType.Equals( DMCompiler.Compiler.DM.DMASTProcStatement ):
                pass
                ast_categories[ ty.BaseType ].append( ty )
            elif ty.BaseType.Equals( DMCompiler.Compiler.DM.DMASTExpression ):
                pass
                ast_categories[ ty.BaseType ].append( ty )
            elif ty.BaseType.Equals( DMCompiler.Compiler.DM.DMASTNode ):
                pass
                ast_categories[ ty.BaseType ].append( ty )
            elif ty.BaseType.Equals( DMCompiler.Compiler.DM.DMASTExpressionConstant ):
                pass
                ast_categories[ ty.BaseType ].append( ty )
            elif ty.BaseType.Equals( DMCompiler.Compiler.DM.DMASTDereference ):
                pass
                ast_categories[ ty.BaseType ].append( ty )
            else:
                raise Exception("unknown base type", ty.FullName, ty.BaseType.FullName)

            for field in ty.GetFields():
                if check_known_type(field.FieldType) is None:
                    raise Exception("unknown field", field.Name, field.FieldType.FullName)

    for k, vs in ast_categories.items():
        print( str(k) )
        for v in vs:
            print( "  ", v)

load_ast_types()
