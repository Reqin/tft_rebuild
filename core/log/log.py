import time
import os
import inspect

max_log_size = 2097152


def print_log(info):
    # 记录时间
    c_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # 分隔符
    separator = ' : '
    # 调用位置
    location = inspect.stack()[1].filename + ' at line ' + str(inspect.stack()[1].lineno)
    # 记录内容
    info = str(info)
    log_content = c_time + separator + location + ' info = ' + info + '\n'
    print(log_content)


def log(info, path='D:\workplace\\tft_rebuild\log\log.txt'):
    # 记录时间
    c_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # 分隔符
    separator = ' : '
    # 调用位置
    location = inspect.stack()[1].filename + ' at line ' + str(inspect.stack()[1].lineno)
    # 记录内容
    info = str(info)
    log_content = c_time + separator + location + ' info = ' + info + '\n'
    open_file_mode = 'a'
    # 若不存在则新建
    if not os.path.exists(path):
        open(path, 'w').close()
    # 清除过大的日志文件
    fsize = os.path.getsize(path)
    if fsize > max_log_size:
        open_file_mode = 'w'

    with open(path, open_file_mode, encoding='utf8') as f:
        f.writelines(log_content)
