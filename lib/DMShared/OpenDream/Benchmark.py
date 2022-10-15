
def get_paths(paths):
    paths.benchmark_source_dir = dream_config.paths.tests_dir / "dm" / "benchmark"
    paths.benchmark_tmp_dir = dream_config.paths.tmp_dir / "benchmark"

def simple_input(benchmark, value):
    input_file = benchmark.input_dir / f'{benchmark.name}.input'
    with Shared.File.open(input_file , "w") as i:
        i.write( str(value) )

def fasta_input(benchmark, value):
    benchmark.set_input( benchmark.ctx.results.get( "fasta", value ) )
    shutil.copy( result.output_file, os.path.join(benchmark.input_dir, benchmark.name + ".input") )

async def simple_benchmark(benchmark):
    if benchmark.compilation.source_modified():
        with Shared.File.open( dream_config.paths.log_dir / "benchmark-compile" / f"{benchmark.id}.txt", "w" ) as f:
            io = {"stdout":f, "stderr":f}
            await benchmark.install.compile( benchmark.test_src, io )
    with Shared.File.open( benchmark_tmp_dir / 'output' / f"{benchmark.id}.out", "w" ) as f:
            io = {"stdout":f, "stderr":f}
            await benchmark.install.run( benchmark.compilation.get_bytecode_file(), io)

class Calibration(object):
    def __init__(self, lo, hi, step):
        self.lo = lo
        self.hi = hi
        self.step = step

    def iter(self):
        return range(self.lo, self.hi+1, self.step)

class BinaryTree(object):
    name = "binary-tree"
    calibrate = Calibration(4, 14, 1)
    set_input = simple_input
    run = simple_benchmark

class FannkuchRedux(object):
    name = "fannkuch-redux"
    calibrate = Calibration(4, 9, 1)
    set_input = simple_input
    run = simple_benchmark

class Fasta(object):
    name = "fasta"
    calibrate = Calibration(4000, 16000, 4000)
    set_input = simple_input
    run = simple_benchmark

class KNucleotide(object):
    name = "k-nucleotide"
    calibrate = Calibration(100, 1000, 100)

class Mandlebrot(object):
    name = "mandlebrot"
    calibrate = Calibration(60, 360, 60)
    set_input = simple_input
    run = simple_benchmark

class ReverseComplement(object):
    name = "reverse-complement"
    calibrate = Calibration(20, 180, 20)

class SpectralNorm(object):
    name = "spectral-norm"
    calibrate = Calibration(40, 240, 40)
    set_input = simple_input
    run = simple_benchmark

async def run_calibration(benchmark, new_compilation):
    benchmark.input_dir = benchmark_tmp_dir
    benchmark.test_src = benchmark_tmp_dir / f"{benchmark.name}.dm"
    benchmark.compilation = new_compilation( benchmark.test_src )
    Shared.refresh_file(benchmark_source_dir / f"{benchmark.name}.dm", benchmark.test_src)

    for input_value in benchmark.calibrate.iter():
        benchmark.set_input(input_value)
        benchmark.id = f"{benchmark.install.name}-{benchmark.name}-{input_value}"
        result = await benchmark.run()

async def opendream_main():
    Shared.sync_folders( benchmark_source_dir / "include", benchmark_tmp_dir )
    async for od_install in iter_od_builds():
        for benchmark in [BinaryTree, FannkuchRedux, Fasta, Mandlebrot, SpectralNorm]:
            start_time = time.time()
            benchmark.args = ""
            benchmark.install = od_install
            await run_calibration( benchmark(), OpenDream.Compilation )
        return

async def byond_main():
    os.chdir( benchmark_source_dir )
    Shared.sync_folders( benchmark_source_dir / "include", benchmark_tmp_dir )
    install = dream_config.byond_installs['514.1566']
    for benchmark in [BinaryTree, FannkuchRedux, Fasta, Mandlebrot, SpectralNorm]:
        start_time = time.time()
        benchmark.install = install
        benchmark.install.postargs = "-trusted"
        await run_calibration( benchmark(), Byond.Compilation )

async def main():
    config = Common.Config(os.path.expanduser("~/dream/config/default.py"))
    config.dirs.app = config.dirs.storage / 'apps' / 'benchmark_opendream'
    config.dirs.app.logs.dm_compiles = config.dirs.app.logs.base / 'dm_compiles'
    Shared.ensure_dirs(config.dirs)
    async for opendream_result in get_opendream_installs(config):
        async for dme_result in get_dme_files(config):
            log_filename = config.dirs.app.logs.dm_compiles / f"{opendream_result['name']}-{dme_result['name']}.txt"
            compile_result = await Common.opendream_compile_dme( opendream_result["install"], dme_result["dme"], log_filename )
