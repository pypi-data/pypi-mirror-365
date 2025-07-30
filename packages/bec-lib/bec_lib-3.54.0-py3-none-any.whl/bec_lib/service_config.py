"""
This module provides a class to handle the service configuration.
"""

import copy
import json
import os
from pathlib import Path

import yaml

from bec_lib.logger import bec_logger

logger = bec_logger.logger

DEFAULT_BASE_PATH = (
    str(Path(__file__).resolve().parent.parent.parent) if "site-packages" not in __file__ else "./"
)

DEFAULT_SERVICE_CONFIG = {
    "redis": {"host": os.environ.get("BEC_REDIS_HOST", "localhost"), "port": 6379},
    "service_config": {
        "file_writer": {
            "plugin": "default_NeXus_format",
            "base_path": os.path.join(DEFAULT_BASE_PATH, "data"),
        },
        "log_writer": {"base_path": os.path.join(DEFAULT_BASE_PATH, "logs")},
    },
    "acl": DEFAULT_BASE_PATH + "/.bec_acl.env",
}


class ServiceConfig:
    def __init__(
        self,
        config_path: str | None = None,
        redis: dict | None = None,
        service_config: dict | None = None,
        config: dict | None = None,
        config_name: str = "server",
        **kwargs,
    ) -> None:
        self.config_path = config_path
        self.config = config if config else {}
        self.config_name = config_name
        if not self.config:
            self._load_config()
        if self.config:
            self._load_urls("redis", required=True)
            self._load_urls("mongodb", required=False)

        self._update_config(service_config=service_config, redis=redis, **kwargs)

        self.service_config = self.config.get(
            "service_config", DEFAULT_SERVICE_CONFIG["service_config"]
        )

    def _update_config(self, **kwargs):
        for key, val in kwargs.items():
            if not val:
                continue
            self.config[key] = val

    def _load_config(self):
        """
        Load the base configuration. There are four possible sources:
        1. A file specified by `config_path`.
        2. An environment variable `BEC_SERVICE_CONFIG` containing a JSON string.
        3. The config stored in the deployment_configs directory, matching the defined config name.
        4. The default configuration.
        """
        if self.config_path:
            if not os.path.isfile(self.config_path):
                raise FileNotFoundError(f"Config file {repr(self.config_path)} not found.")
            with open(self.config_path, "r", encoding="utf-8") as stream:
                self.config = yaml.safe_load(stream)
                logger.info(
                    "Loaded new config from disk:"
                    f" {json.dumps(self.config, sort_keys=True, indent=4)}"
                )
            return
        if os.environ.get("BEC_SERVICE_CONFIG"):
            self.config = json.loads(os.environ.get("BEC_SERVICE_CONFIG"))
            logger.info(
                "Loaded new config from environment:"
                f" {json.dumps(self.config, sort_keys=True, indent=4)}"
            )
            return

        if self.config_name:
            deployment_config_path = os.path.join(
                DEFAULT_BASE_PATH, f"deployment_configs/{self.config_name}.yaml"
            )
            if os.path.exists(deployment_config_path):
                with open(deployment_config_path, "r", encoding="utf-8") as stream:
                    self.config = yaml.safe_load(stream)
                    logger.info(
                        "Loaded new config from deployment_configs:"
                        f" {json.dumps(self.config, sort_keys=True, indent=4)}"
                    )
                return

        self.config = copy.deepcopy(DEFAULT_SERVICE_CONFIG)

    def _load_urls(self, entry: str, required: bool = True):
        config = self.config.get(entry)
        if config:
            return f"{config['host']}:{config['port']}"

        if required:
            raise ValueError(
                f"The provided config does not specify the url (host and port) for {entry}."
            )
        return ""

    @property
    def redis(self):
        return self._load_urls("redis", required=True)

    @property
    def abort_on_ctrl_c(self):
        return self.service_config.get("abort_on_ctrl_c", True)

    def is_default(self):
        """Return whether config is DEFAULT_SERVICE_CONFIG"""
        return self.config == DEFAULT_SERVICE_CONFIG
