from .component import Component, component_config


class Equipment(Component):
    major_field = "name"

    fields = [
        "name",
        "img_path",
        "type",
        "statistics",
        "skill",
        "components"
    ]

    json_fields = [
        "components",
        "statistics"
    ]

    def __init__(self, config):
        self.index = config.index


equipment_config = component_config.equipment
equipment = Equipment(equipment_config)
