from core.winApi.winApi import get_win_cap, get_win_handle, get_win_pos, mouse_left_click
import time
from core.state.state import get_state, get_lineup_state
from lib import logger
from lib import config_parser, config_init
from core.game_components import default_lineup
from core.image.image import com_sim_text_img
import keyboard

engine_config = config_parser(config_init.engine.path)

targets_area = []
for __x, __y in zip(engine_config.default.x, engine_config.default.y):
    targets_area.append(
        (__x, __y, __x + engine_config.default.w, __y + engine_config.default.h)
    )


class Worker:
    target_window_name = engine_config.target_window
    ttf_path = engine_config.ttf_path
    target_win_handle = None
    lineups_index = {
        "early_lineup": "default.lineup.默认_early_lineup",
        "mid_term_lineup": "default.lineup.默认_mid_term_lineup",
        "final_lineup": "default.lineup.默认_final_lineup",
    }
    targets_area = targets_area
    busy = False

    @staticmethod
    def get_target_characters_name() -> [str]:
        # 用于还原状态
        pre_index = default_lineup.index
        default_lineup.index = Worker.lineups_index[get_lineup_state()]
        characters = default_lineup.all()
        default_lineup.index = pre_index
        names = []
        for character in characters:
            names.append(character.character.split().pop())
        return names

    @staticmethod
    def find_target_character_in_window(frame) -> 0 or 1 or 2 or 3 or 4:
        target_characters_name = Worker.get_target_characters_name()
        character_name_images = Worker.get_target_character_name_images(frame)
        which = []
        i = -1
        for character_name_image in character_name_images:
            i += 1
            for target_character_name in target_characters_name:
                score = com_sim_text_img(
                    character_name_image,
                    target_character_name,
                    engine_config.default.h,
                    Worker.ttf_path,
                    (engine_config.default.w, engine_config.default.h)
                )
                if score > 0.95:
                    which.append(i)
                    logger.debug("成功，已匹配，角色名:{},位置:{},score:{}".format(target_character_name, which, score))
                    break
        return which

    @staticmethod
    def click_target_character_in_window(which: 0 or 1 or 2 or 3 or 4) -> None:
        win_loc = get_win_pos(Worker.target_win_handle)
        if not win_loc:
            return
        for loc in which:
            x = engine_config.default.x[loc] + win_loc[0]
            y = engine_config.default.y[loc] + win_loc[1]
            mouse_left_click(x, y)

    @staticmethod
    def get_window_handle() -> int or None:
        return get_win_handle(Worker.target_window_name)

    @staticmethod
    def get_target_win_frame():
        return get_win_cap(Worker.target_win_handle)

    @staticmethod
    def get_target_character_name_images(frame):
        images = []
        for area in Worker.targets_area:
            images.append(frame.crop(area))
        return images

    @staticmethod
    def get_current_state() -> 0 or 1:
        return get_state()

    @staticmethod
    def work():
        # 工作状态是否激活
        if not Worker.get_current_state():
            logger.info("状态未激活，返回")
            return
        # 是否能找到游戏窗口
        Worker.handle = Worker.get_window_handle()
        if not Worker.handle:
            logger.warning("未找到目标窗口，返回")
            time.sleep(5)
            return
        if not (frame := Worker.get_target_win_frame()):
            logger.warning("未获取到窗口画面，返回")
            time.sleep(5)
            Worker.target_win_handle = Worker.get_window_handle()
            return
        # 开始识别
        Worker.busy = True
        which = Worker.find_target_character_in_window(frame)
        Worker.busy = False
        # 对目标进行拾取
        for i in range(2):
            Worker.click_target_character_in_window(which)

    @staticmethod
    def d_work():
        logger.warning("d WORK")
        Worker.work()
        time.sleep(0.1)
        Worker.work()

    @staticmethod
    def morning() -> None:
        keyboard.add_hotkey("d",Worker.d_work)
        while True:
            time.sleep(3)
            Worker.work()
