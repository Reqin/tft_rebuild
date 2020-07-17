import os
import pickle
import json
from lib import logger


def __create_file(path):
    try:
        open(path, 'w', encoding='utf8').close()
        log_info = ' create ' + path
    except:
        log_info = ' fail to create ' + path
    logger.info(log_info)


def __open_file(path, open_type):
    try:
        if not os.path.exists(path):
            __create_file(path)
        f = open(path, open_type)
        return f
    except:
        log_info = ' fail to open ' + path
        logger.info(log_info)
    return None


def __read_byte_then(path, func):
    f = __open_file(path, 'rb')
    content = func(f)
    f.close()
    return content


def __write_byte_with(path, func):
    f = __open_file(path, 'wb')
    func(f)
    f.close()


def __add_byte_with(path, func):
    f = __open_file(path, 'ab')
    func(f)
    f.close()


def __touch(path):
    if os.path.exists(path):
        logger.error("创建失败，已存在的文件，文件路径：{}".format(path))
        return True
    else:
        with open(path, "w") as f:
            f.close()
    return False


def __clear(path):
    if os.path.exists(path):
        with open(path, "w") as f:
            f.write("")
    else:
        logger.error("清空失败，文件不存在，文件路径：{}".format(path))


def read_line(path):
    # 读取单行
    def func(f): return f.readline().decode('utf8')

    return __read_byte_then(path, func)


def read_all(path):
    # 读取整个文件
    def func(f): return f.read().decode('utf8')

    return __read_byte_then(path, func)


def add_line(path, line):
    # 追加一行
    def func(f): return f.write("{}\r\n".format(line).encode("utf8"))

    return __add_byte_with(path, func)


def update_line(path, line_no, line):
    # 更改一行记录
    def func(f):
        pass


def pkl_load(path):
    # 读取pkl文件
    def func(f): return pickle.load(f)

    return __read_byte_then(path, func)


def pkl_dump(obj, path):
    # 写入pkl文件
    def func(f, obj=obj): pickle.dump(obj, f)

    __write_byte_with(path, func)


def load_json(path):
    # 读取json文件
    def func(f): return json.load(f)

    return __read_byte_then(path, func)


def dump_json(obj, path):
    pass
