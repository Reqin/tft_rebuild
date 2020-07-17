from python_json_config import ConfigBuilder

# create config parser
config_builder = ConfigBuilder()
config_parser = config_builder.parse_config
# parse config
config_init = config_builder.parse_config('conf/conf.json')
