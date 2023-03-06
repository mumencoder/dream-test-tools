
from common import *

async def main():
    root_env = Shared.Environment()
    root_env_t = EnvTracker(root_env, "root_env")

    setup_base(root_env)
    root_env_t.print("1")

    config_env = root_env.branch()
    config_env_t = EnvTracker(config_env, "config_env")

    load_config(config_env, open_config())
    config_env_t.print("2")

    root_env.attr.tmp_dir = config_env.attr.tmp_dir.value

    collider_env = root_env.branch()
    collider_env_t = EnvTracker(collider_env, "collider_env")
    builder_opendream(collider_env)
    collider_env_t.print("1")
    generate_ast(collider_env)
    collider_env_t.print("2")
    tokenize_ast(collider_env)
    collider_env_t.print("3")
    unparse_ast(collider_env)
    collider_env_t.print("4")
    compute_ngrams(collider_env)
    collider_env_t.print("5")

    benv = root_env.branch()
    benv_t = EnvTracker(benv, "benv")
    for prop in list(config_env.filter_properties(".byond_main.*")):
        config_env.rebase(".byond_main", ".install", prop, new_env=benv, copy=True)
    benv_t.print("1")

    cenv = benv.branch()
    cenv_t = EnvTracker(cenv, "cenv")
    cenv.attr.compilation.text = collider_env.attr.collider.text
    renv = await byond_compilation(root_env, cenv)
    cenv_t.print("1")

    renv_t = EnvTracker(renv, "renv")
    renv_t.print_local()

    oenv = root_env.branch()

asyncio.run( main() )
