from .spider import Spider
from lib import logger
from selenium.webdriver.common.by import By
from core.game_components import strategy as strategy_controller


class StrategySpider(Spider):
    index = "strategy"

    def __init__(self, config):
        super().__init__(config)
        self.__next_strategy_count = 0

    @staticmethod
    def run(config):
        spider = StrategySpider(config)
        spider.crawl()

    def next_strategy(self):
        # 获取阵容列表
        strategy_list = self.wait_element((By.CLASS_NAME, "lineup-list"))
        strategys = strategy_list.find_elements_by_class_name("lineup-item")
        if self.__next_strategy_count >= len(strategys):
            logger.info("没有找到阵容元素")
            return False
        else:
            target_strategy = strategy_list.find_elements_by_class_name("lineup-item")[self.__next_strategy_count]
            self.__next_strategy_count += 1
            strategy_link = target_strategy.find_element_by_class_name("lineup-link")
            strategy_link.click()
            strategy_detail = self.wait_element((By.CLASS_NAME, "app-wrap"))
            return strategy_detail

    def get_hover_character_name(self):
        return self.browser.find_element_by_class_name(
            "tooltip-champion-summary").find_element_by_class_name("tcs-name").text

    def get_hover_equipment_name(self):
        return self.browser.find_element_by_class_name(
            "tooltip-equipment-summary").find_element_by_class_name("tes-equipment-name").text

    @staticmethod
    def parse_lineup_data(lineup_names, core_characters):
        lineup_items = []
        lineup_item = dict()
        for name in lineup_names:
            lineup_item["character"] = name
            lineup_item["equipment"] = []
            for _character in core_characters:
                if name == _character["name"]:
                    lineup_item["equipment"] = _character["equipment_name"]
            print("lineup_item", lineup_item)
            import copy
            lineup_items.append(copy.deepcopy(lineup_item))
        return lineup_items

    def crawl(self):
        # 进入目标页面
        strategy_name = ""
        self.get_target_page()
        # 切换到S级阵容 只爬取S级阵容
        target_link = self.browser.find_element_by_xpath('//*[@id="appMain"]/div[1]/div/div[1]/div[3]/a[2]')
        target_link.click()
        while strategy := self.next_strategy():
            strategy_data = dict()
            early_lineup_characters_name = []
            mid_term_lineup_characters_name = []
            final_lineup_characters_name = []
            core_characters = []
            thinking = dict()
            strategy_detail_contents = strategy.find_elements_by_class_name("lineup-detail-content")
            for strategy_detail_content in strategy_detail_contents:
                if strategy_detail_content.find_elements_by_class_name("lineup-title") and len(
                        strategy_detail_content.find_elements_by_class_name("lineup-title")) > 0:
                    # 提取最终阵容信息
                    strategy_tile = strategy_detail_content.find_element_by_class_name("lineup-title")
                    strategy_name = strategy_tile.text
                    final_lineup_character_items = strategy_detail_content.find_elements_by_class_name("champion-pic")
                    for final_lineup_character_item in final_lineup_character_items:
                        self.hover(final_lineup_character_item)
                        character_name = self.get_hover_character_name()
                        final_lineup_characters_name.append(character_name)
                    print("最终阵容", final_lineup_characters_name)
                elif "早期过渡" in strategy_detail_content.text:
                    # 提取前期、中期阵容信息和 ”早期过渡“思路
                    # 早期过渡思路
                    thinking_desc = strategy_detail_content.find_element_by_class_name("content-desc").text
                    thinking["早期过渡"] = thinking_desc
                    print("早期过渡", thinking["早期过渡"])
                    # 前期、中期阵容信息
                    lineup_stages = strategy_detail_content.find_elements_by_class_name("lineup-stage")
                    for lineup_stage in lineup_stages:
                        if "前期" == lineup_stage.find_element_by_class_name("lineup-stage-name").text:
                            characters = lineup_stage.find_elements_by_class_name("champion-pic")
                            for character in characters:
                                self.hover(character)
                                character_name = self.get_hover_character_name()
                                early_lineup_characters_name.append(character_name)
                            print("前期阵容", early_lineup_characters_name)
                        if "中期" == lineup_stage.find_element_by_class_name("lineup-stage-name").text:
                            characters = lineup_stage.find_elements_by_class_name("champion-pic")
                            for character in characters:
                                self.hover(character)
                                character_name = self.get_hover_character_name()
                                mid_term_lineup_characters_name.append(character_name)
                            print("中期阵容", mid_term_lineup_characters_name)
                elif "装备分析" in strategy_detail_content.text:
                    # 装备分析 思路
                    thinking["装备分析"] = strategy_detail_content.find_element_by_class_name("lineup-equip-desc").text
                    print("装备分析", thinking["装备分析"])
                    # 核心角色装备
                    core_character_items = strategy_detail_content.find_elements_by_class_name("lineup-equip")
                    i = 0
                    for core_character_item in core_character_items:
                        i += 1
                        print(i)
                        # 核心角色名称
                        character_item = core_character_item.find_elements_by_class_name("champion-pic")
                        if not (character_item and len(character_item) > 0):
                            break
                        character_item = character_item.pop()
                        self.hover(character_item)
                        character_name = self.get_hover_character_name()
                        # 核心角色装备
                        equipment_items = core_character_item.find_elements_by_class_name("component-equipment")
                        equipment_names = []
                        for equipment_item in equipment_items:
                            equipment_item = equipment_item.find_element_by_tag_name("img")
                            self.hover(equipment_item)
                            equipment_name = self.get_hover_equipment_name()
                            equipment_names.append(equipment_name)
                        core_character = {
                            "name": character_name,
                            "equipment_name": equipment_names
                        }
                        core_characters.append(core_character)
                    print("核心人物", core_characters)
                elif "阵容站位" in strategy_detail_content.text:
                    thinking["阵容站位"] = strategy_detail_content.find_element_by_class_name("lineup-location-info").text
                    print(thinking["阵容站位"])
                elif "搜牌节奏" in strategy_detail_content.text:
                    thinking["搜牌节奏"] = strategy_detail_content.find_element_by_class_name("content-desc").text
                    print(thinking["搜牌节奏"])
                elif "克制分析" in strategy_detail_content.text:
                    thinking["克制分析"] = strategy_detail_content.find_element_by_class_name("content-desc").text
                    print(thinking["克制分析"])
                else:
                    logger.debug("数据异常，无匹配项")

            # 数据整理
            strategy_data["name"] = strategy_name

            strategy_data["early_lineup"] = self.parse_lineup_data(
                early_lineup_characters_name,
                core_characters
            )
            print(strategy_data["early_lineup"])
            print(strategy_data["early_lineup"][0])
            strategy_data["mid_term_lineup"] = self.parse_lineup_data(
                mid_term_lineup_characters_name,
                core_characters
            )
            print(strategy_data["mid_term_lineup"])
            print(strategy_data["mid_term_lineup"][0])
            strategy_data["final_lineup"] = self.parse_lineup_data(
                final_lineup_characters_name,
                core_characters
            )
            print(strategy_data["final_lineup"])
            print(strategy_data["final_lineup"][0])
            strategy_data["thinking"] = thinking
            assert False
            strategy_controller.record(strategy_data)

            back_button = strategy.find_element_by_class_name("page-btn-title")
            back_button.click()
        self.wait()
        self.quit()
