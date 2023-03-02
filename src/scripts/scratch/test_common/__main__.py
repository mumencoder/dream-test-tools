
from common import *

print_env(genv, "1")
builder_opendream(genv)
print_env(genv, "2")
generate_ast(genv)
print_env(genv, "3")
tokenize_ast(genv)
print_env(genv, "4")
unparse_ast(genv)
print_env(genv, "5")
compute_ngrams(genv)
print_env(genv, "6")
