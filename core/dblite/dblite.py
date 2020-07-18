"""
@author: Reqin
@desc:  这是此项目的数据驱动程序。
        除了用于程序初始化的配置信息之外，所有文本数据的增、删、查、改必须通过这个这个程序进行。
        此程序的数据规范如下：
        1. 此程序读取 .db 文件
        2. 每一个 .db 文件里包含的数据必须是同一类数据，每一类数据的用途必须严格一致
        3. .db 文件只存储文本数据，且文本数据的意义表征只能是严格的文本，不用于解码等其他操作
        4. .db 文件的第一行是此文件中所有数据的索引,且索引必须为非数字，且不能重复
        5. .db 文件没有严格意义上的数据纵向排列，不能存在两行相同的数据，数据的重复不会被读取，也无法写入重复的数据
        6. .db 文件字段之间使用 英文标点冒号 隔开用于表征和识别字段数据
        7. .db 文件现阶段只进行小文件操作，使用者需要避免 .db 文件过大
        8. 为了更好的鲁棒性 尽量使得每个字段中的值简单化是一个明智的选择
"""
import os
import collections
from core.filePipe.pipe import read_all, add_line
from core.filePipe.pipe import __touch as touch
from core.filePipe.pipe import __clear as clear
from lib import logger
from functools import wraps
from lib import config_init, config_parser


def is_empty_table(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        table = args[0]
        if not table.fields:
            logger.info("执行中止，不能对空表进行此操作，表名:{}，中断参数:{} -- {}，".format(table.name, args, kwargs))
            return []
        else:
            return func(*args, **kwargs)

    return wrapper


class Table:
    def __init__(self, config):
        self.name = config.default_table_name
        self.path = config.path
        self.swap_file_suffix = config.swap_file_suffix
        self.swap_path = self.path + self.swap_file_suffix
        self.encode_type = list
        self.decode_type = str
        self.fields = []
        self.data = []
        self.file_data = read_all(self.path).strip().split(os.linesep)
        self.file_fields = self.file_data[0]
        if not self.file_fields:
            logger.info("读取到空表 path:{}".format(self.path))
        else:
            self.fields = self.__decode(self.file_fields)
            try:
                self.__load_data()
                self.encode_type = self.metadata
            except ValueError as e:
                logger.critical("数据表初始化失败，数据文件损坏，无法读取，错误:{}".format(e))

    def __load_data(self):
        self.metadata = collections.namedtuple(self.name, self.fields)
        for file_line in self.file_data:
            data_line = self.__decode(file_line)
            if len(self.fields) == len(data_line):
                new_data = self.metadata(*data_line)
                if new_data in self.data:
                    logger.warning("表中存在重复的数据,表:{} 数据:{}".format(self.name, data_line))
                else:
                    self.data.append(new_data)
            else:
                logger.warning("表数据异常表:{},数据:{}".format(self.name, file_line))

    # 将每一行的文件数据转为数据表数据
    def __encode(self, data):
        if not isinstance(data, self.encode_type):
            logger.error("数据格式错误，数据:{},标准格式:{}".format(data, self.encode_type))
            return False
        else:
            line = "{}".format(data[0])
            for one in data[1:]:
                line += "!&:{}".format(one)
            return line

    # 将一个数据表记录转为数据表文件标准格式
    def __decode(self, line):
        if not isinstance(line, self.decode_type):
            logger.error("数据格式错误，数据:{},标准格式:{}".format(line, self.decode_type))
            return False
        else:
            return line.split("!&:")

    def __update_file(self):
        touch(self.swap_path)
        clear(self.swap_path)
        for data_line in self.data:
            file_line = self.__encode(data_line)
            add_line(self.swap_path, file_line)
        try:
            os.remove(self.path)
            os.rename(self.swap_path, self.path)
        except Exception as e:
            logger.critical("更新失败，数据文件时出现异常，文件路径:{}，交换路径:{}".format(self.path, self.swap_path))

    def get_fields(self):
        return self.fields

    def create(self, fields):
        if self.data:
            logger.info("失败，无法在未清空的表中创建新表，表文件路径:{}".format(self.path))
            return False
        if add_line(self.path, self.__encode(fields)):
            logger.info("成功，已创建表，表字段:{}".format(fields))

    @is_empty_table
    def clear(self):
        if clear(self.path):
            logger.info("成功，已清空表，表文件路径:{}".format(self.path))
            self.data = []
            self.encode_type = list
            return True
        else:
            logger.info("失败，未清空表，文件异常，表文件路径:{}".format(self.path))
            return False

    @is_empty_table
    def insert(self, fields, values):
        if not isinstance(fields, list) or not isinstance(values, list):
            logger.error("数据格式错误，插入失败，标准格式:{} 未能和字段:{} 数据:{} 完全匹配".format(list, fields, values))
            return 0
        if len(fields) != len(values):
            logger.error("数据长度错误，插入失败，字段:{} 未能和值:{} 完全匹配".format(fields, values))
            return 0
        if fields != self.fields:
            logger.error("数据字段错误，插入失败，标准字段:{} 未能和字段:{} 完全匹配".format(self.fields, fields))
            return 0
        new_data = self.metadata(*values)
        if new_data in self.data:
            logger.warning("不允许数据重复，数据:{} 已存在".format(values))
            return 0
        else:
            line = self.__encode(new_data)
            if line:
                add_line(self.path, self.__encode(new_data))
            else:
                logger.warning("数据编码失败，数据:{}".format(new_data))
            self.data.append(new_data)
            return 1

    # noinspection PyArgumentList
    @is_empty_table
    def update(self, trait, change):
        old_records = self.retrieve(*trait)
        if not old_records:
            return None
        new_records = []
        for old_record in old_records:
            new_value = []
            for field in self.fields:
                if field != change[0]:
                    new_value.append(old_record.__getattribute__(field))
                else:
                    new_value.append(change[1])
            new_record = self.metadata(*new_value)
            new_records.append(new_record)
            self.data[self.data.index(old_record)] = new_record
        if new_records != old_records:
            self.__update_file()
            return 1
        else:
            logger.info("已动作，数据无变化，旧记录:{}，新记录:{}".format(old_records, new_records))
            return 0

    @is_empty_table
    def retrieve(self, field, value):
        records = []
        if field not in self.fields:
            logger.warning("在字段 {} 中查询不存在的字段: {}".format(self.fields, field))
        else:
            records = [one for one in self.data if one.__getattribute__(field) == value]
            if not records:
                logger.info("字段 {} 中未查询到数据: {}".format(field, value))
        return records

    @is_empty_table
    def delete(self, field, value):
        pass

    @is_empty_table
    def all(self):
        return self.data[1:]


def get_table(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = args[0]
        keys = args[1].split(".")
        # 切换数据表所在的数据库
        for key in keys[:-1]:
            if isinstance(db, DB):
                if key in db.dbs:
                    db = db.dbs[key]
                else:
                    logger.error("不存在的数据库索引:{}".format(args[1]))
                    return False
            else:
                logger.critical("错误！数据异常，数据:{} 与 标准数据库数据{} 类型不匹配".format(db, DB))
                return False
        table_name = keys[-1]
        if table_name in db.dbs.keys():
            table = db.dbs[table_name]
            if isinstance(table, Table):
                return func(*args, **kwargs, table=table)
            else:
                logger.critical("错误！数据异常，数据:{} 与 标准数据表数据{} 类型不匹配".format(table, Table))
                return False


        else:
            logger.error("不存在的数据表索引:{}".format(args[1]))
            return None

    return wrapper


class DB:
    type = {
        1: "DB",
        2: "TABLE"
    }

    def __init__(self, config):
        self.config = config
        self.__path = config.path
        self.__suffix = config.suffix
        self.name = config.default_db_name
        self.dbs = {}
        self.__load_data()

    def __load_data(self):
        self.dbs[self.name] = {}
        for item in os.listdir(self.__path):
            path = os.path.join(self.__path, item)
            self.config.path = path
            self.config.default_db_name = item
            if os.path.isdir(path):
                self.dbs[item] = DB(self.config)
            else:
                name, suffix = os.path.splitext(item)
                self.config.default_table_name = name
                if suffix == self.__suffix:
                    self.dbs[name] = Table(self.config)

    @get_table
    def insert(self, index, fields, values, table=None):
        del index
        return table.insert(fields, values)

    @get_table
    def update(self, index, trait, change, table=None):
        del index
        return table.update(trait, change)

    @get_table
    def get_fields(self, index, table=None):
        del index
        return table.get_fields()

    @get_table
    def retrieve(self, index, field, value, table=None):
        del index
        return table.retrieve(field, value)

    @get_table
    def delete(self, index, fields, value, table=None):
        pass

    @get_table
    def all_table_data(self, index, table=None):
        del index
        return table.all()

    @get_table
    def generate_table(self, index, fields, table=None):
        del index
        return table.create(fields)

    @get_table
    def clear_table(self, index, table=None):
        del index
        return table.clear()


db_config = config_parser(config_init.db.path)
default_db_engine = DB(db_config)
