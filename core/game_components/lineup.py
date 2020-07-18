from .component import Component, component_config
from .character import character as character_controller
from .equipment import equipment as equipment_controller
from lib import logger


class Lineup(Component):
    major_field = "character"
    fields = [
        "character",
        "equipment_1",
        "equipment_2",
        "equipment_3"
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
        pass


lineup_config = component_config.default_lineup
default_lineup = Lineup(lineup_config)
