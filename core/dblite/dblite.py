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
from core import log
from core import read_all


class DB:
    def __init__(self, file_path, name='metadata'):
        """
        :param file_path: 需要读取的 .db 文件路径
        """
        data_file = read_all(file_path).split('\r\n')
        self.fields = data_file[0].split(':')
        metadata = collections.namedtuple(name, self.fields)
        self.data = [metadata(*data_line.split(':')) for data_line in data_file[1:]]

    def query(self, filed, value):
        if filed not in self.fields:
            log('查询不存在的字段')
            return None
        else:
            many = []
            for one in self.data:
                if value == one.__getattribute__(filed):
                    many.append(one)
            if many is []:
                log('未查询到匹配的数据')
            return many

    def all(self):
        return self.data
