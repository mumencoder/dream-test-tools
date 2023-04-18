
from .imports import *

def get_file(filename, default_value=None):
    if not os.path.exists(filename):
        return default_value
    with open(filename, "rb") as f:
        return f.read()

def put_file(filename, data):
    with open(filename, "wb") as f:
        f.write(data)

def maybe_from_pickle(data, default_value=None):
    try:
        return pickle.loads(data)
    except:
        return default_value

def parse_csv(l):
    return [ s.strip() for s in l.split(',') if s.strip() != "," ]