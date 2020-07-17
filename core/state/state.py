from lib import config_init, config_builder
from core import DB


def set_state(state):
    with open(config['engine.path_state'], 'w') as f:
        f.write(str(state))


def get_state():
    with open(config['engine.path_state'], 'rb') as f:
        state = f.readline().decode()
        return int(state)
