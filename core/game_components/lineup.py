from .component import Component, component_config
from .character import character as character_controller
from .equipment import equipment as equipment_controller
from lib import logger
from core import default_db_engine
import copy


class Lineup(Component):
    major_field = "character"
    fields = [
        "character",
        "equipment",
    ]

    character_fields = [
        "character"
    ]

    equipment_fields = [
        "equipment_1",
        "equipment_2",
        "equipment_3"
    ]

    def __init__(self, config):
        self.index = config.index
        self.characters = []

    def get_allys(self):
        allys = self.all()
        for ally in allys:
            logger.debug(ally)
            characters = character_controller.get(ally.__getattribute__(self.major_field))
            equipments_name = [ally.__getattribute__(equipment_field) for equipment_field in self.equipment_fields]
            equipments = [equipment_controller.get(equipment_name) for equipment_name in equipments_name if
                          equipment_name]
            logger.debug(equipments_name)


class LineupController:
    @staticmethod
    def record_lineup(lineup_name, lineup_data):
        index = "{}.{}".format(lineup_config.index, lineup_name)
        new_table_config = copy.deepcopy(default_lineup_config)
        new_table_config.index = index
        new_lineup = Lineup(new_table_config)
        new_lineup.establish()
        i = 0
        for data in lineup_data:
            res = new_lineup.new(data)
            if res:
                i += 1
        return index, i


lineup_config = component_config.lineup
default_lineup_config = component_config.default_lineup
default_lineup = Lineup(default_lineup_config)
