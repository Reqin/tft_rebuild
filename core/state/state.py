from lib import config_init, config_parser
from core import default_db_engine
from lib import logger

__config = config_parser(config_init.state.path)
__index = __config.gui.index
__major_key = __config.gui.major_key
__name = __config.gui.name


def set_state(state):
    return default_db_engine.update(__index, [__major_key, __name], {"state": state})


def get_state():
    return default_db_engine.retrieve(__index, __major_key, __name).pop()[1]


def set_lineup_state(lineup_name):
    return default_db_engine.update(__index, [__major_key, "lineup"], {"state": lineup_name})


def get_lineup_state():
    return default_db_engine.retrieve(__index, __major_key, "lineup").pop()[1]
