from .component import Component, component_config


class Character(Component):
    major_field = "name"
    fields = [
        "name",
        "head_image",
        "character_image",
        "skill_1",
        "skill_2",
        "skill_3",
        "skill_4",
        "feature1",
        "feature2",
        "feature3",
        "feature4",
        "feature6",
    ]

    def __init__(self, config):
        self.index = config.index


character_config = component_config.character
character = Character(character_config)
