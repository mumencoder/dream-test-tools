
async def run_opendream_pnet():
    cenv = tenv.branch()

    settings = DMCompilerSettings()
    settings.Files = List[String]()
    settings.Files.Add( str(tenv.attr.compilation.dm_file_path) )

    prevout = Console.Out
    stdout = System.IO.StringWriter(System.Text.StringBuilder())
    Console.SetOut(stdout)
    try:
        cenv.attr.compilation.returncode = DMCompiler.Compile(settings)
    except Exception as e:
        cenv.attr.compilation.returncode = False
    Console.SetOut(prevout)
    cenv.attr.compilation.log = stdout.ToString()
    with open( cenv.attr.test.path / 'opendream.compile.stdout.txt', "w" ) as f:
        f.write( cenv.attr.compilation.log )

    renv = None
    if cenv.attr.compilation.returncode is True:
        renv = tenv.branch()
        renv.attr.run.dm_file_path = DMShared.OpenDream.Run.get_bytecode_file( cenv.attr.compilation.dm_file_path )
        dreamman.LoadJson( str(renv.attr.run.dm_file_path) )

        try:
            t = tests.RunNewTest()
            success = t.Item1
            rval = t.Item2
            renv.attr.run.log = str(t.Item3)
        except Exception as e:
            pass

        if os.path.exists( renv.attr.test.path / 'test.out.json'):
            with open( renv.attr.test.path / 'test.out.json', "r" ) as f:
                try:
                    renv.attr.run.output = json.load(f)
                except json.decoder.JSONDecodeError:
                    pass
            os.remove( renv.attr.test.path / 'test.out.json')
    
    return (cenv, renv)

async def run_opendream():
    cenv = tenv.branch()
    
    cenv.attr.build.dir = Shared.Path( env.attr.collider.config["opendream"]["repo_dir"] ) / 'DMCompiler'
    cenv.attr.process.stdout = open(cenv.attr.test.path / 'opendream.compile.stdout.txt', "w")
    await DMShared.OpenDream.Compilation.compile( cenv )
    with open(cenv.attr.test.path / "opendream.compile.returncode.txt", "w") as f:
        f.write( str(cenv.attr.compilation.returncode) )
    cenv.attr.process.stdout.close()

    if cenv.attr.compilation.returncode == 0:
        renv = tenv.branch()
        renv.attr.build.dir = Shared.Path( env.attr.collider.config["opendream"]["repo_dir"] ) / 'bin' / 'Content.Server'
        renv.attr.process.stdout = open(renv.attr.test.path / 'opendream.run.stdout.txt', "w")
        renv.attr.run.dm_file_path = DMShared.OpenDream.Run.get_bytecode_file( cenv.attr.compilation.dm_file_path )
        renv.attr.run.args = {}
        await DMShared.OpenDream.Run.run(renv)
        renv.attr.process.stdout.close()
    
    return (cenv, renv)