from .spider import Spider
from lib import logger
from selenium.webdriver.common.by import By
from core.game_components import equipment
import os
from .downloader import download


class EquipmentSpider(Spider):
    index = "equipment"

    def __init__(self, config):
        super().__init__(config)
        self.__next_strategy_count = 0

    @staticmethod
    def run(config):
        spider = EquipmentSpider(config)
        spider.crawl()

    def get_hover_equipment_name(self):
        return self.browser.find_element_by_class_name(
            "tooltip-equipment-summary").find_element_by_class_name("tes-equipment-name").get_attribute('innerText')

    def get_hover_equipment_desc(self):
        return self.browser.find_element_by_class_name(
            "tooltip-equipment-summary").find_element_by_class_name("tes-equipment-desc").get_attribute('innerText')

    def crawl(self):
        self.get_target_page()
        equipment.reestablish()

        img_foundation_dir = self.config.target.equipment.image.foundation
        img_combination_dir = self.config.target.equipment.image.combination

        switch_buttons = self.browser.find_element_by_class_name("filter-box").find_elements_by_tag_name("a")
        # 基础装备
        switch_buttons[0].click()
        equipment_list = self.browser.find_element_by_class_name("equipment-list").find_elements_by_tag_name("img")
        equipment_item = {}
        for item in equipment_list:
            self.hover(item)
            equipment_name = self.get_hover_equipment_name()
            equipment_desc = self.get_hover_equipment_desc()
            equipment_img_url = item.get_attribute("src")
            equipment_img_path = os.path.join(img_foundation_dir, "{}.png".format(equipment_name))
            download(equipment_img_path, equipment_img_url)
            logger.info("执行中，正在下载资源，url:{},path:{}".format(equipment_img_url, equipment_img_path))
            # 数据整理
            equipment_item["name"] = equipment_name
            equipment_item["type"] = "foundation"
            equipment_item["img_path"] = equipment_img_path
            equipment_item["statistics"] = [equipment_desc]
            equipment_item["skill"] = ""
            print(equipment_item)
            self.wait(1)
            equipment.new(equipment_item)
        # 成型装备
        switch_buttons[1].click()
        equipment_list = self.browser.find_element_by_class_name("equipment-list").find_elements_by_tag_name("img")
        equipment_item = {}
        for item in equipment_list:
            self.hover(item)
            equipment_name = self.get_hover_equipment_name()
            equipment_desc = self.get_hover_equipment_desc()
            equipment_img_url = item.get_attribute("src")
            equipment_img_path = os.path.join(img_combination_dir, "{}.png".format(equipment_name))
            download(equipment_img_path, equipment_img_url)
            logger.info("执行中，正在下载资源，url:{},path:{}".format(equipment_img_url, equipment_img_path))
            # 数据整理
            equipment_item["name"] = equipment_name
            equipment_item["type"] = "combination"
            equipment_item["img_path"] = equipment_img_path
            equipment_item["statistics"] = []
            equipment_item["skill"] = equipment_desc
            equipment.new(equipment_item)

        self.wait()
        self.quit()
