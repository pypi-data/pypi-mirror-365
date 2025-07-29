import os
import sys
import copy
import stat
import json
import shutil
import requests
from pathlib import Path
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from .logs import logger
from .recipe import Recipe
from .server import TestServer
from .message import KafkaMessage
from .defaults import (
    default_kafka,
    default_producer,
    default_service,
    default_canary,
)

class TestConfig:
    def __init__(
        self,
        recipes: list[Recipe],
        working_dir: str = "",
        compose_file: str = "docker-compose.yaml",
        **kwargs
    ):
        self._top_dir = Path.cwd()
        self._working_dir = working_dir
        self._compose_file = compose_file
        self._recipes = recipes
        self._attrs = kwargs
        self._forward_to = None

    def set_forward_address(self, address: str):
        self._forward_to = address

    def set_top_dir(self, top_dir: Path):
        self._top_dir = top_dir

    def recipes(self) -> list[Recipe]:
        return self._recipes

    def working_dir(self) -> Path:
        return self._top_dir.joinpath(self._working_dir)

    def compose_file(self) -> Path:
        return self.working_dir().joinpath(self._compose_file)

    def local_cfg_dir(self) -> Path:
        return self.working_dir().joinpath(Recipe.LOCAL_CFG_DIR)

    def to_dict(self, script_path: str|None = None) -> dict:
        self.local_cfg_dir().mkdir(parents = True, exist_ok = True)

        result = copy.deepcopy(self._attrs)
        result["services"] = result.get("services", {})
        result["services"]["kafka"] = default_kafka() | result["services"].get("kafka", {})

        canary_config = self._add_canary(result.get("canary", True))
        self._add_producer(result, canary_config)
        self._add_service(result, canary_config)
        self._add_recipes(result, canary_config)
        return result

    def to_yaml(self) -> str:
        return dump(self.to_dict(), Dumper = Dumper)

    def build_docker_compose(self):
        self.compose_file().write_text(self.to_yaml())

    def cleanup(self):
        if self.local_cfg_dir().exists():
            shutil.rmtree(self.local_cfg_dir())

    def _download_canary(self, canary_config: dict) -> bool:
        username, token = "", ""
        try:
            username = os.environ[canary_config["gitlab"]["username"]]
            token = os.environ[canary_config["gitlab"]["token"]]
        except Exception as e:
            logger.warning(f"Unable to get gitlab credentials "
                           f"in order to download autotest-canary: {e}")
            return False

        version = ""
        if "version" in canary_config:
            version = canary_config["version"]
        else:
            version = default_canary()["version"]
            logger.warning(f"Version for autotest-canary not found, "
                           f"defaulting to {version}")

        logger.debug("Downloading autotest-canary...")
        response = requests.get(
            "https://git.apps.eo4eu.eu/api/v4/projects/154/packages/generic"
            f"/autotest-canary/{version}/autotest-canary",
            auth = (username, token)
        )

        if response.status_code != 200:
            logger.warning(f"Failed to download autotest-canary: "
                           f"HTTP status code {response.status_code}")
            return False

        out_path = self.local_cfg_dir().joinpath("autotest-canary")
        out_path.write_bytes(response.content)
        out_path.chmod(out_path.stat().st_mode | stat.S_IEXEC)
        return True

    def _add_canary(self, canary_config: dict|bool) -> dict|bool:
        if canary_config == False:
            return False
        if canary_config == True:
            canary_config = default_canary()

        downloaded = self._download_canary(canary_config)
        if downloaded:
            return canary_config
        else:
            logger.warning(f"Unable to download autotest-canary, disabling feature...")
            return False

    def _add_producer(self, result: dict, canary_config: dict|bool):
        # write the input messages
        at_prod_dir = self.local_cfg_dir().joinpath("at_prod")
        if at_prod_dir.exists():
            shutil.rmtree(at_prod_dir)
        at_prod_dir.mkdir(parents = True, exist_ok = True)
        for recipe in self._recipes:
            for topic, message in recipe.inputs().items():
                at_prod_dir.joinpath(topic).write_text(json.dumps(message))

        condition = "service_healthy" if canary_config != False else "service_started"
        result["services"]["at_prod"] = default_producer(
            config_dir = self.local_cfg_dir().joinpath("at_prod"),
            depends_on = {
                recipe.name(): {"condition": condition}
                for recipe in self._recipes
            }
        ) | result["services"].get("at_prod", {})

    def _add_service(self, result: dict, canary_config: dict|bool):
        at_serv_dir = self.local_cfg_dir().joinpath("at_serv")
        if at_serv_dir.exists():
            shutil.rmtree(at_serv_dir)
        at_serv_dir.mkdir(parents = True, exist_ok = True)
        at_serv_dir.joinpath("autotest_service.json").write_text(
            json.dumps(self._get_service_config(canary_config))
        )

        result["services"]["at_serv"] = default_service(
            config_dir = self.local_cfg_dir().joinpath("at_serv"),
        ) | result["services"].get("at_serv", {})

    def _add_recipes(self, result: dict, canary_config: dict|bool):
        for recipe in self._recipes:
            recipe_name = recipe.name()
            recipe_conf = recipe.to_dict(
                working_dir = self.working_dir(),
                canary_config = canary_config
            )
            if recipe_name in result["services"]:
                result["services"][recipe_name] = recipe_conf | result["services"][recipe_name]
            else:
                result["services"][recipe_name] = recipe_conf

            for top_level, config in recipe.also_add().items():
                if top_level in result:
                    result[top_level] |= config
                else:
                    result[top_level] = config

    def _get_service_config(self, canary_config: dict|bool) -> dict:
        has_canary = canary_config != False
        create_topics = set()
        recipes = {}
        for recipe in self._recipes:
            recipe_name = recipe.name()
            recipes[recipe_name] = {"match": {}}
            if has_canary:
                canary_topic = f"{recipe_name}-canary_"
                recipes[recipe_name]["canary"] = {
                    "topic": canary_topic,
                    **canary_config["options"],
                }
                create_topics.add(canary_topic)

            for topic, message in recipe.outputs().items():
                create_topics.add(topic)
                recipes[recipe_name]["match"][topic] = [message]
            for topic in recipe.inputs().keys():
                create_topics.add(topic)
        result = {
            "create_topics": list(create_topics),
            "recipes": recipes,
        }
        if self._forward_to is not None:
            result["forward_to"] = self._forward_to

        return result
