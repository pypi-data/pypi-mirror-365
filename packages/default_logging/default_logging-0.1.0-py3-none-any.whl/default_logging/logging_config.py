import logging.config
import yaml
import os
from importlib import resources

def setup_logging(config_path=None):
    """
    Set up logging configuration.

    Args:
        config_path (str, optional): Path to a YAML config file. If None, uses the default config.
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
