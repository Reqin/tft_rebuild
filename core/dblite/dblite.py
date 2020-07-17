"""
@author: Reqin
@desc:  这是此项目的数据驱动程序。
        除了用于程序初始化的配置信息之外，所有文本数据的增、删、查、改必须通过这个这个程序进行。
        此程序的数据规范如下：
        1. 此程序读取 .db 文件
        2. 每一个 .db 文件里包含的数据必须是同一类数据，每一类数据的用途必须严格一致
        3. .db 文件只存储文本数据，且文本数据的意义表征只能是严格的文本，不用于解码等其他操作
        4. .db 文件的第一行是此文件中所有数据的索引,且索引必须为非数字，且不能重复
        5. .db 文件没有严格意义上的数据纵向排列，所以可以存在两行严格相同的数据，在这里被看作是数据的重复
        6. .db 文件字段之间使用 英文标点冒号 隔开用于表征和识别字段数据
        7. .db 文件现阶段只进行小文件操作，使用者需要避免 .db 文件过大
        8. 为了更好的鲁棒性 尽量使得每个字段中的值简单化是一个明智的选择
"""
import collections
from core.filePipe.pipe import read_all
from lib import logger
import os
from functools import wraps


def is_empty_table(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        table = args[0]
        if table.data is None:
            logger.info("table:{} 为空".format(table.name))
            return 0
        else:
            return func(*args, **kwargs)

    return wrapper


class Table:
    def __init__(self, path, name='metadata'):
        """
        :param file_path: 需要读取的 .db 文件路径
        """
        # self.path = path
        self.name = name
        data_file = read_all(path).split('\r\n')
        self.fields = data_file[0].split(':')
        if self.fields == ['']:
            logger.info("读取到空表 path:{}".format(path))
            self.data = None
        else:
            metadata = collections.namedtuple(name, self.fields)
            data_lines = [line.split(":") for line in data_file[1:]]
            self.data = [metadata(*data_line) for data_line in data_lines if
                         len(self.fields) == len(data_line)]

    @is_empty_table
    def create(self, filed, value):
        pass

    @is_empty_table
    def update(self, filed, value):
        pass

    @is_empty_table
    def retrieve(self, filed, value):
        if filed not in self.fields:
            logger.warning("在字段 {} 中查询不存在的字段: {}".format(self.fields, filed))
            return None
        else:
            many = [one for one in self.data if one.__getattribute__(filed) == value]
            if not many:
                logger.info("字段 {} 中未查询到数据: {}".format(filed, value))
            return many

    @is_empty_table
    def delete(self, filed, value):
        pass

    def all(self):
        return self.data


class DB:
    type = {
        1: "DB",
        2: "TABLE"
    }

    def __init__(self, path, suffix, default_db_name="default_db"):
        """
        :param config: 查看lib.config
        """
        self.__path = path
        self.__suffix = suffix
        self.__default_db_name = default_db_name
        self.dbs = {}
        self.__load_data()

    def __load_data(self, first=False):
        self.dbs[self.__default_db_name] = {}
        for item in os.listdir(self.__path):
            path = os.path.join(self.__path, item)
            if os.path.isdir(path):
                self.dbs[item] = DB(path, self.__suffix, default_db_name=item)
            else:
                name, suffix = os.path.splitext(item)
                if suffix == self.__suffix:
                    self.dbs[self.__default_db_name][name] = Table(path, name=name)

    def create(self, table_name, filed, value):
        pass

    def update(self, table_name, filed, value):
        pass

    def retrieve(self, table_name, filed, value):
        pass

    def delete(self, table_name, filed, value):
        pass
