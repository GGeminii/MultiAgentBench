import os

from ruamel.yaml import YAML
from marble.utils.logger import get_logger

logger = get_logger("READ_CODING_CONFIG")
def read_coding_config():
    config_path = "marble/configs/coding_config/coding_config.yaml"
    if not os.path.exists(config_path):
        logger.error(f"Coding config file not found at {config_path}")
        return None

    yaml = YAML()
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.load(f)
    return config