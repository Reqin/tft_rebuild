from .spider import Spider
from lib import logger
import time

class LineupSpider(Spider):
    def __init__(self, config):
        super().__init__(config)

    @staticmethod
    def run(config):
        spider = LineupSpider(config)
        spider.crawl()

    def crawl(self):
        self.browser.get(self.config.target.lineup.url)
        # self.browser.get(self.config.target.lineup.url)
        target_link = self.browser.find_element_by_xpath('//*[@id="appMain"]/div[1]/div/div[1]/div[3]/a[2]')
        target_link.click()
        lineups = self.browser.find_elements_by_class_name('lineup-item')
        logger.debug(lineups)
        for lineup in lineups:
            lineup.find_element_by_class_name("lineup-expand").click()
            time.sleep(1)
            lineup.click()
            logger.debug(lineup.text)
        self.wait()
        self.quit()
