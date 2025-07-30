import logging.config
import yaml
import os
from importlib import resources
from typing import Optional

def setup_logging(config_path: Optional[str] = None):
    """
    Set up logging configuration from a YAML file.

    If a config path is provided, loads logging configuration from that file.
    Otherwise, loads the default configuration bundled with the package.

    For file-based handlers, ensures the log file directory exists.

    Args:
        config_path (Optional[str]): Path to a YAML config file. If None, uses the default config.

    Raises:
        FileNotFoundError: If the specified config file does not exist.
        yaml.YAMLError: If the YAML config is invalid.
        Exception: For other errors during logging configuration setup.
    """
    if config_path:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    else:
        with resources.files("default_logging").joinpath("logging_config.yaml").open("r") as f:
            config = yaml.safe_load(f)

        if 'handlers' in config:
            for handler_name, handler_config in config['handlers'].items():
                if handler_config.get('class') == 'logging.handlers.RotatingFileHandler' or \
                handler_config.get('class') == 'logging.FileHandler':
                    filename = handler_config.get('filename')
                    if filename:
                        os.makedirs(os.path.dirname(filename), exist_ok=True)

    logging.config.dictConfig(config)
