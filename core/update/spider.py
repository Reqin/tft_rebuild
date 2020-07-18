from lib import config_init
from lib import logger
from selenium import webdriver
import os
import time


class Spider:
    def __init__(self, config):
        self.config = config
        chrome_options = webdriver.ChromeOptions()
        # 使用headless无界面浏览器模式
        options = config.chrome_options.__getattr__(config_init.stage)
        for option in options:
            chrome_options.add_argument(option)
        if isinstance(config.driver_path, str) and os.path.exists(config.driver_path):
            logger.info("正在加载爬虫驱动:{}".format(config.driver_path))
            self.browser = webdriver.Chrome(config.driver_path, chrome_options=chrome_options)
        else:
            logger.info("驱动加载失败，路径错误，错误的路径:{}".format(config.driver_path))

    @staticmethod
    def wait(s=10000):
        time.sleep(s)

    def quit(self):
        self.browser.quit()
