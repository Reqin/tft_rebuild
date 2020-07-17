from python_json_config import ConfigBuilder

# create config parser
__config_builder = ConfigBuilder()

# parse config
config_init = __config_builder.parse_config('conf/conf.json')
config_db = __config_builder.parse_config(config_init.db.path)
