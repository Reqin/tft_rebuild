import os
import pickle
import json
from core import log


def __create_file(path):
    try:
        open(path, 'w', encoding='utf8').close()
        log_info = ' create ' + path
    except:
        log_info = ' fail to create ' + path
    print(555)
    print(log_info)
    log(log_info)


def __open_file(path, open_type):
    if not os.path.exists(path):
        __create_file(path)
    try:
        f = open(path, open_type)
        return f
    except:
        log_info = ' fail to open ' + path
        log(log_info)
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


def read_line(path):
    # 读取单行
    def func(f): return f.readline().decode('utf8')

    return __read_byte_then(path, func)


def read_all(path):
    # 读取整个文件
    def func(f): return f.read().decode('utf8')

    return __read_byte_then(path, func)


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
