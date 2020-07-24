from .component import Component, component_config
from .lineup import LineupController, Lineup
from lib import logger
import json


class Strategy(Component):
    major_field = "name"
    fields = [
        "name",
        "early_lineup",
        "mid_term_lineup",
        "final_lineup",
        "thinking",
    ]
    lineup_fields = [
        "early_lineup",
        "mid_term_lineup",
        "final_lineup",
    ]

    json_fields = [
        "thinking"
    ]

    def __init__(self, config):
        self.index = config.index
        logger.debug(self.index)

    def record(self, strategy):
        assert isinstance(strategy, dict) and strategy.get(self.major_field, False), "契约错误"
        strategy_data = dict()

        for field in self.fields:
            if field in self.lineup_fields:
                lineup_name = "{}_{}".format(strategy[self.major_field], field)
                lineup_index, record_line_count = LineupController.record_lineup(lineup_name, strategy.get(field, ""))
                logger.info("成功，已生成并记录表内容，表:{}，记录了:{}条数据".format(lineup_name, record_line_count))
                data = lineup_index
            else:
                data = strategy.get(field, "")
                if field == "thinking":
                    data = json.dumps(data, ensure_ascii=False)
            strategy_data[field] = data
        self.new(strategy_data)


strategy_config = component_config.strategy
strategy = Strategy(strategy_config)
