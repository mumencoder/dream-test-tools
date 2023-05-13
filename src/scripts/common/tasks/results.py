
from ..imports import *

def save_test(tenv):
    required_attrs = [
        '.collider.text',
        '.collider.compile_predict',
        '.collider.ast',
        '.collider.ast_tokens',
    ]
    optional_attrs = [
        '.byond.compile.stdout_text',
        '.byond.compile.returncode',
        '.byond.objtree.stdout_text',
        '.byond.objtree.returncode',
        '.collider.ngram_info',
    ]

    marshall_fns = []
    #marshall_fns.append( (".collider.ast", lambda env, v: DreamCollider.AST.marshall(v) ) )
    #marshall_fns.append( ('.collider.ast_tokens', lambda env, v: DreamCollider.Shape.marshall(v) ) )

    data = {}
    for attr in required_attrs:
        if not tenv.has_attr(attr):
            raise Exception(f'missing required attr {attr}')
        data[attr] = tenv.get_attr( attr )
    for attr in optional_attrs:
        if not tenv.has_attr(attr):
            continue
        data[attr] = tenv.get_attr( attr )

    for attr, marshall_fn in marshall_fns:
        if attr not in data:
            continue
        data[attr] = marshall_fn(tenv, data[attr])
        
    return pickle.dumps(data)

def load_test(tenv, p):
    marshall_fns = []
    #marshall_fns.append( (".collider.ast", lambda env, v: DreamCollider.AST.unmarshall(v) ) )
    #marshall_fns.append( ('.collider.ast_tokens', lambda env, v: list( DreamCollider.Shape.unmarshall(v, env.attr.collider.ast) ) ) )

    d = pickle.loads(p)
    for name, value in d.items():
        tenv.set_attr(name, value)

    for attr, marshall_fn in marshall_fns:
        if tenv.has_attr(attr):
            tenv.set_attr(attr, marshall_fn(tenv, tenv.get_attr(attr)) )

    return tenv

import DreamCollider