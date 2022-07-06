
## Setup

The compose file defines a mount with a placeholder path. Change this to where you want the output files to go on your host machine.

## Building

```docker build --tag dtt -f centos.Dockerfile . ```

## Running

```docker compose run dtt python3.8 dtt.py run_byond```

```docker compose run dtt python3.8 dtt.py run_opendream```

If a 'dotnet restore' process hangs try adding the --network=host option to the 'docker build' step.
