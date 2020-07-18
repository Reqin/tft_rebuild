from lib import config_init, config_parser
from .LineupSpider import LineupSpider

update_config = config_parser(config_init.updater.path)


def update():
    LineupSpider.run(update_config)
    pass
