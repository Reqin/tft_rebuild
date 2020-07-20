from lib import config_init, config_parser
from .StrategySpider import StrategySpider

update_config = config_parser(config_init.updater.path)


def update():
    StrategySpider.run(update_config)
    pass
