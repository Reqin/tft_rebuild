from .character import character
from .equipment import equipment
from .lineup import default_lineup
from .strategy import strategy
from lib import logger
from lib.config import config_init, config_parser

component_config = config_parser(config_init.game_component.path)
