
## Setup

The compose file defines a mount with a placeholder path. Change this to where you want the output files to go on your host machine.

## Building

```docker build --tag dtt -f centos.Dockerfile . ```

## Running local tests

```docker compose run dtt python3.8 dtt.py run_local <run_id> <repo_path>```

run_id determines where various run specific output files go, arbitrary value determined by user
repo_path is a path on the docker container. Add a path in the compose file so the container can see your host filesystem repos.

## Troubleshooting

If a 'dotnet restore' process hangs try adding the --network=host option to the 'docker build' step.
