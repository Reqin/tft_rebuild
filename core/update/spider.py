from lib import config_init
from lib import logger
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import os
import time


class Spider:
    index = ""

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
            self.browser.implicitly_wait(5)
        else:
            logger.info("驱动加载失败，路径错误，错误的路径:{}".format(config.driver_path))

    def wait_element(self, locator):
        return WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(locator))

    def text_from_class(self, class_name, driver=None, timeout=2, time_pulse=0.1):
        if not driver:
            driver = self.browser
        text = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))).get_attribute('innerText')
        if timeout <= 0:
            self.wait()
            raise TimeoutError
        if not text.strip():
            print(text)
            timeout -= time_pulse
            time.sleep(time_pulse)
            text = self.text_from_class(timeout)
        return text

    @staticmethod
    def wait(s=10000):
        time.sleep(s)

    def hover(self, element):
        webdriver.ActionChains(self.browser).move_to_element(element).perform()

    def quit(self):
        self.browser.quit()

    def get_target_page(self):
        url = self.config.target.__getattr__(self.index).url
        self.browser.get(url)
