from .component import Component, component_config


class Equipment(Component):
    major_field = "name"
    fields = [
        "name",
        "image",
        "skill_1",
        "skill_2",
        "skill_3"
    ]

    def __init__(self, config):
        self.index = config.index


equipment_config = component_config.equipment
equipment = Equipment(equipment_config)
