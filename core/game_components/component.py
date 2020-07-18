# from interface import Interface
from lib import config_init, config_parser
from core import default_db_engine
from lib import logger
from functools import wraps


def check_fields(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        component = args[0]
        data = args[1]
        data_fields = data.keys()
        for field in data_fields:
            if field not in component.fields:
                logger.warning("执行中止，存在不匹配的字段，输入字段:{} 声明字段:{}".format(field, component.fields))
                return False
        return func(*args, **kwargs)

    return wrapper


class Component:

    @check_fields
    def new(self, data):
        data_value = []
        data_fields = data.keys()
        for filed in self.fields:
            if filed in data_fields:
                value = data[filed]
            else:
                value = ""
            data_value.append(value)
        return default_db_engine.insert(self.index, self.fields, data_value)

    @check_fields
    def get_by_filed(self, data):
        field, value = data.popitem()
        return default_db_engine.retrieve(self.index, field, value)

    def establish(self):
        return default_db_engine.generate_table(self.index, self.fields)

    def destroy(self):
        return default_db_engine.clear_table(self.index)

    def reestablish(self):
        self.destroy()
        self.establish()

    def all(self):
        return default_db_engine.all_table_data(self.index)

    def get(self, value):
        return self.get_by_filed({self.major_field: value})


component_config = config_parser(config_init.game_component.path)
