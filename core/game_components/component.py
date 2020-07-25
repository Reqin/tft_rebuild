from lib import config_init, config_parser
from core import default_db_engine
from lib import logger
from functools import wraps
import json
import copy

component_config = config_parser(config_init.game_component.path)


def check_fields(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        args = copy.deepcopy(args)
        component = args[0]
        data = args[1]
        data_fields = data.keys()
        for field in data_fields:
            if field not in component.fields:
                logger.warning("执行中止，存在不匹配的字段，输入字段:{} 声明字段:{}".format(field, component.fields))
                return False
        return func(*args, **kwargs)

    return wrapper


def json_field_encode(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        args = copy.deepcopy(args)
        component = args[0]
        data = args[1]
        data_fields = data.keys()
        for field in component.json_fields:
            if field in data_fields:
                json_s = json.dumps(data[field], ensure_ascii=False)
            else:
                json_s = json.dumps(None, ensure_ascii=False)
            args[1][field] = json_s
        return func(*args, **kwargs)

    return wrapper


class Component:
    major_field = ""
    fields = []
    lineup_fields = []
    json_fields = []

    @check_fields
    @json_field_encode
    def new(self, data):
        data_value = []
        for filed in self.fields:
            if filed in data.keys():
                value = data[filed]
            else:
                value = ""
            data_value.append(value)
        return default_db_engine.insert(self.index, self.fields, data_value)

    def parse_record(self, record):
        record_dict = record._asdict()
        for field in record_dict.keys():
            if field in self.json_fields:
                try:
                    record_dict[field] = json.loads(record_dict[field])
                except json.decoder.JSONDecodeError:
                    logger.critical("错误！，json解析时数据未初始化，数据:{}".format(record_dict[field]))
        record = record._make(record_dict.values())
        return record

    def copy(self,index_pairs):
        return default_db_engine.copy(index_pairs)

    def parse_records(self, records):
        cache_records = []
        for record in records:
            cache_records.append(self.parse_record(record))
        return cache_records

    @check_fields
    def get_by_filed(self, data):
        field, value = data.popitem()
        records = self.pure_get_by_filed(field, value)
        if records:
            records = self.parse_records(records)
        return records

    @json_field_encode
    def update(self, data, major_key_value):
        is_updated = default_db_engine.update(self.index, [self.major_field, major_key_value], data)
        if is_updated:
            return self.get(major_key_value)
        else:
            logger.warning("警告，更新失败，数据异常，数据:{}".format(data))
        # is_deleted = self.lose(major_key_value)
        # if is_deleted:
        #     data.update({self.major_field: major_key_value})
        #     is_inserted = self.new(data)
        #     if is_inserted:
        #         return self.get(major_key_value)
        #     else:
        #         logger.warning("警告，更新失败，新数据生成失败，数据:{}".format(data))
        #         return False
        # else:
        #     logger.warning("警告，更新失败，原数据删除失败，主值:{}".format(major_key_value))
        #     return False

    def establish(self):
        return default_db_engine.generate_table(self.index, self.fields)

    def destroy(self):
        return default_db_engine.clear_table(self.index)

    def reestablish(self):
        self.destroy()
        self.establish()

    def all(self):
        records = default_db_engine.all_table_data(self.index)
        return self.parse_records(records)

    def get(self, value):
        records = self.get_by_filed({self.major_field: value})
        if isinstance(records, list):
            return records.pop()
        return False

    def pure_get(self, value):
        return self.pure_get_by_filed(self.major_field, value).pop()

    def pure_get_by_filed(self, field, value):
        records = default_db_engine.retrieve(self.index, field, value)
        if not records:
            logger.info("执行完毕，没有查询到记录,参数:{}".format({field: value}))
            return False
        return records

    def lose(self, major_filed_value):
        logger.debug(major_filed_value)
        record = self.pure_get(major_filed_value)
        logger.debug(record)
        logger.debug(self.index)
        default_db_engine.delete(self.index, record)
        return record
