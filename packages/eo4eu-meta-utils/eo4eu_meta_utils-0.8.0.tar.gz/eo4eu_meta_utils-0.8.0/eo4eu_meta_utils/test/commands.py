import subprocess
from pathlib import Path
from importlib import import_module
from importlib.util import spec_from_file_location, module_from_spec

from .server import TestServer, ServerFinished
from .config import TestConfig
from .logs import logger


def import_config(args) -> TestConfig:
    config_path = Path.cwd().joinpath(args.file)
    if not config_path.is_file():
        raise FileNotFoundError(f"Failed to find config file {args.file}")

    spec = spec_from_file_location(
        config_path.stem.replace("-", "_"),
        config_path
    )
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    config = module.CONFIG
    config.set_top_dir(config_path.parent)
    return config


def build(args, config: TestConfig):
    """eo-test build|b [-f|--file?=eo-test.py]
    Builds the docker compose file and all related dependencies
    needed for the mock tests, as specified in --file.
    examples:
        eo-test build
            builds using ${PWD}/eo-test.py
        eo-test b -f other-eo-test.py
            builds using ${PWD}/other-eo-test.py
    """
    logger.debug(f"building {config.compose_file()}...")
    config.build_docker_compose()


def run(args, config: TestConfig):
    """eo-test run|r [-f|--file?=eo-test.py]
    (Optionally) builds and runs the mock tests
    examples:
        eo-test run
            runs using ${PWD}/eo-test.py
        eo-test r -f other-eo-test.py
            runs using ${PWD}/other-eo-test.py
        eo-test r --no-rebuild
            runs using ${PWD}/eo-test.py without rebuilding the configuration
    """
    # FIXME: connect to localhost server from inside
    # docker compose
    # config.set_forward_address(TestServer.ADDRESS)
    build(args, config)

    docker_compose_path = config.compose_file()
    subprocess.run([
        "docker", "compose",
        "-f", docker_compose_path,
        "up",
        "-d"
    ])
    subprocess.run([
        "docker", "compose",
        "-f", docker_compose_path,
        "logs",
        "at_serv",
        "--no-log-prefix",
        "--follow",
        "--tail", "10"
    ])
    # try:
    #     TestServer.serve()
    # except ServerFinished:
    #     return
    # except Exception as e:
    #     logger.error(f"Unexpected error: {e}")


def clean(args, config: TestConfig):
    """eo-test clean|c [-f|--file?=eo-test.py]
    Cleans up test artifacts and shuts down running containers
    examples:
        eo-test clean
            cleans using ${PWD}/eo-test.py
        eo-test c -f other-eo-test.py
            cleans using ${PWD}/other-eo-test.py
    """
    config.cleanup()

    docker_compose_path = config.compose_file()
    subprocess.run([
        "docker", "compose",
        "-f", docker_compose_path,
        "down",
    ])


HELP_ALL = """eo-test: A command-line utility for running tests on components.
         It accepts a config file written in Python which defines
         "mock" tests; these are simulations of the real component
         running conditions, using a local docker compose file
         which sets up a kafka server and other dependencies.
Usage: eo-test [command] [options...]
Commands: help  | h
          build | b
          run   | r
          clean | c
Use eo-test help [command] to get a help blurb for individual commands
"""

def help(cmd_dict, cmd_name_dict, *commands: str) -> str:
    """eo-test help|h [command...]
    Prints help messages
    """
    if len(commands) == 0:
        return HELP_ALL

    for command in commands:
        return cmd_dict[cmd_name_dict[command]].__doc__


cmd_dict = {
    "help":  help,
    "build": build,
    "run":   run,
    "clean": clean,
}

cmd_name_dict = {
    "help":  "help",
    "build": "build",
    "run":   "run",
    "clean": "clean",
    "h":     "help",
    "b":     "build",
    "r":     "run",
    "c":     "clean",
}
