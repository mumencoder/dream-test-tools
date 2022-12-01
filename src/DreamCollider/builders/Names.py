
from ..common import *
from ..model import *

def validate_name(name):
    if name in AST.keywords:
        return False
    return True        

def randomVarName():
    letters = random.randint(2,3)
    vn = ""
    for i in range(0, letters):
        vn += random.choice(string.ascii_lowercase)
    return vn

def randomProcName():
    letters = random.randint(2,3)
    vn = ""
    for i in range(0, letters):
        vn += random.choice(string.ascii_lowercase)
    return vn

def randomString(lo, hi):
    letters = random.randint(lo,hi)
    vn = ""
    for i in range(0, letters):
        vn += random.choice(string.ascii_lowercase)
    return vn