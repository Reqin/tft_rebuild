from core import default_db_engine
from lib import config_init, config_parser
from lib import logger
from interface import implements
from .component import Component


class Character(implements(Component)):

    def __init__(self):
        self.config = config_parser(config_init.game_component.path)
        self.index = self.config.component.character.index
        pass

    def create(self, traits):
        default_db_engine.insert(self.index, list(traits.keys()), list(traits.values()))
        pass

    def get(self, value):
        return self.get_by_trait(self.config.major_key, value)

    def get_by_trait(self, key, value):
        return default_db_engine.retrieve(self.index, key, value)

    def set_trait(self, key, value):
        pass


character = Character()
