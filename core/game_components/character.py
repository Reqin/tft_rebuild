from .component import Component, component_config


class Character(Component):
    major_field = "name"
    fields = [
        "name",
        "skill",
        "price",
        "statistics",
        "status",
        "img_head_path",
        "img_character_path"
    ]

    json_fields = [
        "statistics",
        "status",
    ]

    def __init__(self, config):
        self.index = config.index


character_config = component_config.character
character = Character(character_config)
