from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint
import traceback
import logging

from .commands import import_config, cmd_dict, cmd_name_dict
from .logs import logger

command_dict = {
    "build": False,
    "deploy": True,
}

def run():
    parser = ArgumentParser(add_help = False)
    parser.add_argument("commands", type = str, nargs = "*")
    parser.add_argument("--file", "-f", type = str, default = "eo-test.py")
    parser.add_argument("--debug", "-d", action = "store_true")

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    commands = args.commands
    if len(commands) < 1:
        logger.error("Need at least 1 command")
        return

    command, rest = commands[0], commands[1:]
    try:
        command = cmd_name_dict[command]
    except KeyError:
        logger.critical(f"Command \"{command}\" not recognized. "
                        "Use eo-test help for a list of available commands")
        return

    cmd = cmd_dict[command]
    if command == "help":
        print(cmd(cmd_dict, cmd_name_dict, *rest))
        return

    config = None
    try:
        config = import_config(args)
    except Exception as e:
        logger.critical(f"Failed to read config: {e}")
        if args.debug:
            logger.critical(traceback.fmt_exc())
        return

    try:
        cmd(args, config)
    except Exception as e:
        logger.critical(f"Error: {e}")
        if args.debug:
            logger.critical(traceback.format_exc())
