from .spider import Spider
from lib import logger
from selenium.webdriver.common.by import By
from core.game_components import character
import os
from .downloader import download


class CharacterSpider(Spider):
    index = "character"

    def __init__(self, config):
        super().__init__(config)
        self.__next_character_count = 0

    @staticmethod
    def run(config):
        spider = CharacterSpider(config)
        spider.crawl()

    def next_character(self):
        # 获取人物列表
        character_item_list_page = self.wait_element((By.CLASS_NAME, "page-champion"))
        character_item_list = character_item_list_page.find_elements_by_class_name("champion-item-pic")
        if self.__next_character_count >= len(character_item_list):
            logger.info("没有找到人物元素")
            return False
        else:
            character_item_list[self.__next_character_count].click()
            self.__next_character_count += 1
            return True

    def crawl(self):
        self.get_target_page()
        character.reestablish()

        img_character_dir = self.config.target.character.image.character
        img_head_dir = self.config.target.character.image.head

        while self.next_character():

            # 等待加载
            self.wait_element((By.CLASS_NAME, "app-page-content"))
            # 数据
            character_data = dict()
            # character_name = ""
            # character_skill = ""
            character_statistics = dict()
            character_status = []
            # 人物名字
            character_name = self.text_from_class("champion-name")
            # 人物技能
            character_skill = self.browser.find_element_by_class_name("skill-desc").text
            # 人物属性
            character_statistics_box = self.browser.find_element_by_class_name("detail-info-2")
            character_statistics_detail_box = character_statistics_box.find_element_by_class_name("detail-box")
            character_statistics_text = character_statistics_detail_box.find_element_by_class_name(
                "detail-info-desc").text
            character_statistics_list = character_statistics_text.split("\n")
            for character_statistics_item in character_statistics_list:
                print(character_statistics_item)
                character_statistics_item_detail = character_statistics_item.split("：")
                print(character_statistics_item_detail)
                character_statistics[character_statistics_item_detail[0]] = character_statistics_item_detail[1].split(
                    "/")
            # 人物费用
            character_price = character_statistics_box.find_element_by_class_name("detail-price").text
            # 人物羁绊
            character_status_box = self.browser.find_element_by_class_name("detail-info-3")
            character_status_detail_boxes = character_status_box.find_elements_by_class_name("detail-box")
            for detail_box in character_status_detail_boxes:
                status_value = detail_box.find_element_by_class_name("detail-info-title").text
                character_status.append(status_value)

            # 人物头像和人物闪照
            character_image_box = self.browser.find_element_by_class_name("detail-info-1")
            character_img_character_box = character_image_box.find_element_by_class_name("champion-big-pic")
            # 解析资源链接
            character_img_character_url = "https:{}".format(
                character_img_character_box.get_attribute("style").split("\"")[1])
            character_img_head_box = character_image_box.find_element_by_tag_name("img")
            character_img_head_url = "{}".format(character_img_head_box.get_attribute("src"))
            # 生成路径
            img_character_path = os.path.join(img_character_dir, "{}.png".format(character_name))
            img_head_path = os.path.join(img_head_dir, "{}.png".format(character_name))
            download(img_character_path, character_img_character_url)
            logger.info("执行中，正在下载资源，url:{},path:{}".format(character_img_character_url, img_character_path))
            download(img_head_path, character_img_head_url)
            logger.info("执行中，正在下载资源，url:{},path:{}".format(character_img_head_url, img_head_path))
            # self.wait()
            import json

            # 整理数据
            character_data["name"] = character_name
            character_data["skill"] = character_skill
            character_data["price"] = character_price
            character_data["statistics"] = character_statistics
            # logger.debug()
            character_data["status"] = character_status
            character_data["img_head_path"] = img_head_path
            character_data["img_character_path"] = img_character_path
            print(character_data)
            character.new(character_data)
            self.wait(0.5)
            back_btn = self.browser.find_element_by_class_name("icon-arrow-right")
            back_btn.click()
        self.wait()
        self.quit()
