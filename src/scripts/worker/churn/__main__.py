
from common import *

def count_existing(env):
    return len(os.listdir( env.attr.churn_dir ))

def trim_tests(env):
    test_ids = os.listdir( env.attr.churn_dir )
    count = len(test_ids)
    print(f"trimming {count} tests")
    if count > 100000:
        keeps = test_ids[0:100000]
        for test_id in test_ids:
            if test_id not in keeps:
                shutil.rmtree( env.attr.churn_dir / test_id )

async def main():
    root_env = base_env()
    while True:
        renv = await dmsource_all_tasks(root_env)
        test_id = Shared.Random.generate_string(24)

        with open( root_env.attr.churn_dir / test_id / 'byond_compile.pickle', 'wb') as f:
            f.write( save_test(renv.attr.benv) )

        if random.random() < (1/10000.0):
            trim_tests(root_env)

asyncio.run( main() )