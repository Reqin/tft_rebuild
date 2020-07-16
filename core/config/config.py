from modules import log
from modules.filePipe.pipe import load_json
import os


class Config:
    def __init__(self, value={}):
        if type({}) is type(value):
            self.value = value
        else:
            self.value = {}

    def __getitem__(self, key_line):
        cfg = self.value
        try:
            # 注意非字符型keyLine传入的排错
            for key in key_line.split('.'):
                cfg = cfg[key]
        except KeyError as E:
            info = ' config ' + str(key_line) + ' is not an initialization '
            log(info)
            cfg = None
        return cfg

    # def __setitem__(self, key_line, value):
    #     keys = key_line.split('.')
    #     c_value = self.value
    #     try:
    #         for i in range(len(keys) - 1):
    #             c_value = c_value[keys[i]]
    #         c_value[keys[i + 1]] = value
    #     except KeyError as E:
    #         info = ' 配置值错误: ' + key_line + '=' + str(value)


dir_config = './user/configs/'
format_config = '.json'


def get_config(dir_conf=dir_config, format_conf=format_config):
    default_conf = {}
    # 读取所有配置文件
    for root, dirs, files in os.walk(dir_conf):
        for path_file in files:
            name, file_type = os.path.splitext(path_file)
            if file_type == format_conf:
                path = root + path_file
                config = load_json(path)
                default_conf[name] = config
    # 实例化配置类
    default_conf = Config(default_conf)
    return default_conf


default_config = get_config()
