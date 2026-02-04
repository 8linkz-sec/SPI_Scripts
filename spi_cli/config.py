import configparser
import logging
import os
import sys

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.ini")


def load_config(config_path=None):
    """Load configuration from config.ini and return a dict with host, username, password."""
    path = config_path or DEFAULT_CONFIG_PATH
    logger.debug("Loading config from: %s", path)

    if not os.path.exists(path):
        print(f"Error: Config file not found: {path}", file=sys.stderr)
        print("Copy config.ini.example to config.ini and fill in your credentials.", file=sys.stderr)
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(path)

    try:
        section = config["reversinglabs"]
    except KeyError:
        print("Error: [reversinglabs] section missing in config.ini", file=sys.stderr)
        sys.exit(1)

    required = ("host", "username", "password")
    result = {}
    for key in required:
        value = section.get(key)
        if not value or value.startswith("your_"):
            print(f"Error: '{key}' not configured in config.ini", file=sys.stderr)
            sys.exit(1)
        result[key] = value

    logger.debug("Config loaded: host=%s, username=%s", result["host"], result["username"])
    return result
