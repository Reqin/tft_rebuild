from lib import config_init, config_parser
from core import default_db_engine
from lib import logger
from functools import wraps
import json


def check_fields(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        component = args[0]
        data = args[1]
        data_fields = data.keys()
        for field in data_fields:
            if field not in component.fields:
                logger.warning("执行中止，存在不匹配的字段，输入字段:{} 声明字段:{}".format(field, component.fields))
                return False
        return func(*args, **kwargs)

    return wrapper


def json_adapt(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        component = args[0]
        data = args[1]
        data_fields = data.keys()
        for field in data_fields:
            if field in component.fields:
                data[field] = json.dumps(data[field], ensure_ascii=False)
        return func(*args, **kwargs)

    return wrapper


class Component:
    major_field = ""
    fields = []
    lineup_fields = []
    json_fields = []

    @check_fields
    def new(self, data):
        data_value = []
        data_fields = data.keys()
        for filed in self.fields:
            if filed in data_fields:
                value = data[filed]
            else:
                value = ""
            data_value.append(value)
        return default_db_engine.insert(self.index, self.fields, data_value)

    @check_fields
    def get_by_filed(self, data):
        field, value = data.popitem()
        records = default_db_engine.retrieve(self.index, field, value)
        parsed_records = []
        for record in records:
            record = record._asdict()
            for json_field in self.json_fields:
                if json_field in record.keys():
                    record[json_field] = json.loads(record[json_field])
            parsed_records.append(record)
        return parsed_records

    def establish(self):
        return default_db_engine.generate_table(self.index, self.fields)

    def destroy(self):
        return default_db_engine.clear_table(self.index)

    def reestablish(self):
        self.destroy()
        self.establish()

    def all(self):
        return default_db_engine.all_table_data(self.index)

    def get(self, value):
        return self.get_by_filed({self.major_field: value}).pop()


component_config = config_parser(config_init.game_component.path)

a = {'name': '【暗星之王归来】6暗星2刺客2狙神',
     'early_lineup': [{'character': '永恒梦魇 魔腾', 'equipment': []}, {'character': '永恒梦魇 魔腾', 'equipment': []},
                      {'character': '永恒梦魇 魔腾', 'equipment': []}, {'character': '永恒梦魇 魔腾', 'equipment': []}],
     'mid_term_lineup': [{'character': '影流之主 劫', 'equipment': []}, {'character': '影流之主 劫', 'equipment': []},
                         {'character': '影流之主 劫', 'equipment': []}, {'character': '影流之主 劫', 'equipment': []},
                         {'character': '影流之主 劫', 'equipment': []}, {'character': '影流之主 劫', 'equipment': []}],
     'final_lineup': [{'character': '天启者 卡尔玛', 'equipment': []}, {'character': '天启者 卡尔玛', 'equipment': []},
                      {'character': '天启者 卡尔玛', 'equipment': []}, {'character': '天启者 卡尔玛', 'equipment': []},
                      {'character': '天启者 卡尔玛', 'equipment': []}, {'character': '天启者 卡尔玛', 'equipment': []},
                      {'character': '天启者 卡尔玛', 'equipment': []}, {'character': '天启者 卡尔玛', 'equipment': []},
                      {'character': '天启者 卡尔玛', 'equipment': []}],
     'thinking': {'早期过渡': '出门可抢大剑，攻速，腰带均可。可以2刺客，梦魇带小丑装备打工，也可以女警带小丑装备，卡牌带泽拉斯装备打工。主要看谁先2星，用质量高的即可。前期如有狂徒可以给皇子，帮助稳血过度。',
                  '装备分析': '优先做小丑装备：春哥，饮血必备，有火炮最好，没有就羊刀也可以玩。后期靠暗星和饮血续航耗死对手。其次泽拉斯：水银必备，有鬼书和羊刀最好。鬼书来打同行的饮血小丑和女团的奶妈回血。如没鬼书就帽子，法爆也可以玩。烬的装备和小丑的散件雷同，一般不可能有这么多装备。故如果小丑装备先齐了，烬就剩啥用啥，或后期选秀拿成品，窃贼手套不错。如果爆的是烬的装备，就主养烬，小丑做挂件即可。看装备来灵活决定谁是大哥。如果不养小丑，就不用凑2刺客，9人口可以上锤石，猴子，或一个法师，凑2重装，2法师都可以。单挂锤石可以拉很多替补单位上来，死了都可以叠加暗星的BUFF收益，给到大哥身上。',
                  '阵容站位': '如上图：卡尔玛牵泽拉斯在一边，皇子靠过来给泽拉斯加攻速，一定要注意吃到皇子的攻速圈，皇子不能给对面怪拉走，被拉就下移皇子位置。璐璐保护，晕跳过来的刺客。烬和寒冰2个狙神在另一边，小丑和鱼人跳对面C位。特别是打扎堆一起的女团，鱼人跳过去R很大收益。如果对面有刺客，泽拉斯和卡尔玛要躲着换边站，记得带皇子和璐璐一起换边。有春哥的烬可以给刺客跳。',
                  '搜牌节奏': '前期不D牌，速8找泽拉斯。7人口如果质量不够，可以小D一波。如果感觉血量危险，也不够上8找到泽拉斯，或者就没泽拉斯装备。就放弃6暗星，走4暗星，主养小丑，烬。带皇子、洛、寒冰、卡尔玛、索拉卡、鱼人。走2圣盾，2刺客，2狙神，2星神，2秘术的拼多多路线。争前4吃分，也有机会吃鸡。',
                  '克制分析': '泽拉斯和鱼人的AOE，小丑的切入和续航都好打女团。对手是同行比你强，卡你牌或很胡的源计划，特别是带刺客转职的刀妹，冰心艾克跳到泽拉斯可以限制和秒杀，一定站位躲刀妹，其他阵容都可以打。后期决赛圈，如果打女团就用鱼人，打同行或物理输出阵容，就用艾克去减对面攻速，刚好这2个人装备也通用。'}}
