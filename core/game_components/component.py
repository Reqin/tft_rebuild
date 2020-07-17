from interface import Interface


class Component(Interface):
    def create(self, traits):
        pass

    def get_by_trait(self, key, value):
        pass

    def set_trait(self, key, value):
        pass
