# coding:utf8
import os
import time
import PyHook3
import pythoncom
import tkinter as tk
from PIL import ImageTk, Image
from threading import Thread
from core.state.state import set_state
from core.win.ScrollFrame import ScrollableFrame
from core.game_components import character as character_controller
from core.game_components import strategy
from core.game_components import equipment as equipment_controller
from core.game_components import default_lineup as lineup_controller
from lib import logger
from lib import config_init, config_parser
from core.game_components import component_config
from core.winApi import get_cursor_pos
import tkinter.font as tf


def start_main_window():
    main_win = MainGui()
    main_win.mainloop()


def t_font(family="", **kwargs):
    return tf.Font(family=family, **kwargs)


class MainGui(tk.Tk):
    def __init__(self):
        super().__init__()
        # 加载配置文件
        self.gui_config = config_parser(config_init.user.path).gui
        # 初始化资源
        # 这里是所有的人物资源
        self.characters = dict()
        # 用作存储全局的人物头像
        # 字典类型 {
        #   "name":...
        #   "img":加载好的pillow img
        # }
        self.head_img = dict()
        # 所有的装备资源
        self.equipments = dict()
        # 用作存储全局的装备图片
        # 字典类型 {
        #   "name":...
        #   "img":加载好的pillow img
        # }
        self.equipment_img = dict()
        # 用作策略缓存的默认策略
        self.temporary_strategy = {
            "lineups": {
                "early_lineup": dict(),
                "mid_term_lineup": dict(),
                "final_lineup": dict(),
            },
            "thinking": "",
        }
        # 阵容索引字符串
        self.lineup_index = {
            "early_lineup": "",
            "mid_term_lineup": "",
            "final_lineup": "",
        }
        # 加载资源
        self.load_resource()

        # 初始化窗口
        # 主窗口
        # 主窗口所有角色按钮
        self.character_check_button = dict()
        # 当前阵容窗口
        self.win_temporary_strategy = tk.Toplevel()
        # 当前阵容窗口标题栏
        self.win_temporary_strategy_titles = {
            "early_lineup": None,
            "mid_term_lineup": None,
            "final_lineup": None,
            "thinking": None,
        }
        # 当前阵容焦点
        self.lineup_focus = ""
        # 角色详情窗口
        self.win_character_info = tk.Toplevel()
        # 角色详情滚动窗口
        self.hide_win(self.win_character_info)
        self.win_character_info_frame = {
            "character_head_img": None,
            "character_name": None,
            "character_cost": None,
            "character_status": None,
            "character_skill": None,
            "character_statistics": None,
        }
        # 当前阵容窗口可滑动主frame
        self.win_temporary_strategy_content_frames = {
            "early_lineup": {
                "main": None,
                "items": dict()
            },
            "mid_term_lineup": {
                "main": None,
                "items": dict()
            },
            "final_lineup": {
                "main": None,
                "items": dict()
            },
            "thinking": {
                "main": None,
                "text": None
            },
        }
        # 装备列表窗口
        self.win_equipment_list = tk.Toplevel()
        self.hide_win(self.win_equipment_list)
        self.win_equipment_list_frame = None
        # 装备详情窗口
        self.win_equipment_info = tk.Toplevel()
        self.hide_win(self.win_equipment_info)
        self.win_equipment_info_frame = {
            "combination": {
                "img": None,
                "name": None,
                "skill": None
            },
            "foundation": [
                {
                    "img": None,
                    "name": None
                },
            ]
        }
        # 在lineup中最近一次点击的ally元素，其中包含character.name和equipment_button
        self.focus_ally = dict()
        # 窗口是否置顶
        self.top = False
        # 用于判断是否激活主窗口
        self.is_active = True
        # 用于判断当前窗口是否置顶
        self.is_win_topmost = False
        self.build()
        # 用于展示的窗口
        self.update()

    def load_resource(self):
        self.load_characters()
        self.load_head_img()
        self.load_equipments()
        self.load_equipment_img()
        self.load_temporary_strategy()

    def load_characters(self):
        for character in character_controller.all():
            self.characters[character.name] = character

    def load_head_img(self):
        for character in self.characters.values():
            character_head_image_path = character.img_head_path
            photo = Image.open(character_head_image_path)
            photo = photo.resize((self.gui_config.default.win_main.item.photo.width,
                                  self.gui_config.default.win_main.item.photo.height),
                                 Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(photo)
            self.head_img[character.name] = photo

    def load_equipments(self):
        for equipment in equipment_controller.all():
            self.equipments[equipment.name] = equipment

    def load_equipment_img(self):
        for equipment in self.equipments.values():
            equipment_img_path = equipment.img_path
            photo = Image.open(equipment_img_path)
            photo = photo.resize((self.gui_config.default.win_equipments_list.image_size.x,
                                  self.gui_config.default.win_equipments_list.image_size.y),
                                 Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(photo)
            self.equipment_img[equipment.name] = photo

    @staticmethod
    def allys_list2dict(_list_data):
        _dict_data = dict()
        for one in _list_data:
            _dict_data[one.character] = one
        return _dict_data

    def load_temporary_strategy(self):
        temporary_strategy = strategy.get(component_config.temporary_strategy.record_index)
        # 默认阵容文件初始化
        if not temporary_strategy:
            logger.warning("执行中，默认阵容未初始化，开始初始化:{}".format(component_config.temporary_strategy.record_index))
            strategy.record({strategy.major_field: component_config.temporary_strategy.record_index})
            self.load_temporary_strategy()
        # 前期阵容
        lineup_controller.index = temporary_strategy.early_lineup
        self.lineup_index["early_lineup"] = temporary_strategy.early_lineup
        self.temporary_strategy["lineups"]["early_lineup"] = self.allys_list2dict(lineup_controller.all())
        # 中期阵容
        lineup_controller.index = temporary_strategy.mid_term_lineup
        self.lineup_index["mid_term_lineup"] = temporary_strategy.mid_term_lineup
        self.temporary_strategy["lineups"]["mid_term_lineup"] = self.allys_list2dict(lineup_controller.all())
        # 后期阵容
        lineup_controller.index = temporary_strategy.final_lineup
        self.lineup_index["final_lineup"] = temporary_strategy.final_lineup
        self.temporary_strategy["lineups"]["final_lineup"] = self.allys_list2dict(lineup_controller.all())
        # 运营思路
        thinking_text = ""
        for thinking_name in temporary_strategy.thinking:
            thinking_text = thinking_text + "{}：\n{}\n\n".format(thinking_name,
                                                                 temporary_strategy.thinking[thinking_name])
        self.temporary_strategy["thinking"] = thinking_text

    def load_lineups(self):
        self.lineup_index["early_lineup"] = self.temporary_strategy.early_lineup
        self.lineup_index["mid_term_lineup"] = self.temporary_strategy.mid_term_lineup
        self.lineup_index["final_lineup"] = self.temporary_strategy.final_lineup
        self.load_lineup(self.lineup_index["early_lineup"])
        self.load_lineup(self.lineup_index["mid_term_lineup"])
        self.load_lineup(self.lineup_index["final_lineup"])

    def load_lineup(self, index):
        lineup_controller.index = index
        allys = lineup_controller.all()
        for ally in allys:
            self.final_lineup_allys[ally.character] = ally

    @staticmethod
    def lineup_get_ally(index, character):
        lineup_controller.index = index
        lineup_item = {"character": character.name}
        lineup_controller.new(lineup_item)
        return lineup_controller.get(character.name)

    def build(self):
        # 窗口构建
        # 主窗口
        self.build_win_main()
        # 当前策略窗口
        self.build_win_temporary_strategy()
        # 全部阵容窗口
        self.build_lineups_frame()
        # 运营思路窗口
        self.build_thinking_text_frame()
        # 装备概览窗口
        self.build_win_equipment_list()
        # 人物详情窗口
        self.build_win_character_info()
        # 装备详情窗口
        self.build_win_equipment_info()
        # 切换到最终阵容界面
        self.click_strategy_frame_title("final_lineup")
        # 监听键盘
        # self.listenKeyboard()
        # 激活主
        self.active()

    def build_lineups_frame(self):
        logger.debug(self.temporary_strategy)
        for lineup_name in self.temporary_strategy["lineups"]:
            self.build_lineup_frame(lineup_name)

    def build_lineup_frame(self, lineup_name):
        for name in self.temporary_strategy["lineups"][lineup_name]:
            self.character_check_button[name].state.set(True)
            self.add_lineup_frame_item(lineup_name, name)

    def build_thinking_text_frame(self):
        self.win_temporary_strategy_content_frames["thinking"]["text"].config(text=self.temporary_strategy["thinking"])
        return

    def show_lineup_frame(self, lineup_name):
        for character_name in self.character_check_button:
            if character_name in self.temporary_strategy["lineups"][lineup_name].keys():
                if self.character_check_button[character_name].state.get():
                    pass
                else:
                    self.character_check_button[character_name].state.set(True)
            else:
                if self.character_check_button[character_name].state.get():
                    self.character_check_button[character_name].state.set(False)

    def build_win_main(self):
        self.iconbitmap(self.gui_config.default.win_main.ico)
        self.attributes("-alpha", self.gui_config.default.win_main.alpha)
        width = self.gui_config.default.win_main.x
        height = self.gui_config.default.win_main.y
        geo_conf = str(width) + 'x' + str(height)
        self.geometry(geo_conf)
        geo_conf = '+' + str(self.gui_config.default.win_main.migration.x) + \
                   '+' + str(self.gui_config.default.win_main.migration.y)
        self.geometry(geo_conf)
        self.resizable(width=self.gui_config.default.win_main.resizable.x,
                       height=self.gui_config.default.win_main.resizable.y)
        # 动态布局计算
        # 或许不该使用动态计算的布局,而是把布局全做进配置文件中
        item_frame_width = self.gui_config.default.win_main.item.width
        pad_x = (width % item_frame_width) // 2
        bg_frame = tk.Frame(self,
                            bg=self.gui_config.default.win_main.bg_color.default,
                            width=self.gui_config.default.win_main.x,
                            height=self.gui_config.default.win_main.y)
        main_frame = tk.Frame(bg_frame,
                              bg=self.gui_config.default.win_main.bg_color.default,
                              width=width,
                              height=height)
        bg_frame.grid_propagate(0)
        bg_frame.grid(
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )
        main_frame.grid_propagate(0)
        main_frame.grid(
            padx=pad_x,
            sticky=(tk.N, tk.E, tk.S, tk.W),
        )
        self.build_win_main_menu()
        self.build_win_main_frame(main_frame)

    def build_win_main_menu(self):
        win_main_menu = tk.Menu(self)
        win_main_menu.add_cascade(
            label="显示已选", command=lambda: self.show_win(self.win_temporary_strategy)),
        win_main_menu.add_cascade(
            label="隐藏已选", command=lambda: self.hide_win(self.win_temporary_strategy))
        # 自定义阵容
        strategy_menu = tk.Menu(win_main_menu, tearoff=0)
        win_main_menu.add_cascade(label="自定义阵容", menu=strategy_menu)
        strategy_menu.add_command(label='导入', command=self.import_strategy_from_file)
        strategy_menu.add_command(label='导出', command=self.export_strategy)
        strategy_menu.add_command(label='刷新', command=self.refresh_strategy)
        strategy_menu.add_separator()
        # TODO
        strategies = strategy.all()
        for one_strategy in strategies:
            if one_strategy.name == "默认":
                continue
            strategy_menu.add_command(
                label=one_strategy.name, command=lambda x=one_strategy.name: self.import_strategy_from_name(x))
        win_main_menu.add_cascade(label="全部取消", command=self.reject_all)
        win_main_menu.add_cascade(label="我全都要", command=self.select_all)
        win_main_menu.add_cascade(label="激活/冻结拿牌功能（快捷键：“F8 ”）",
                                  command=self.change_state_then_title)
        if self.is_win_topmost:
            menu_topmost_label = "取消窗口置顶（快捷键：“F11”）"
        else:
            menu_topmost_label = "设置窗口置顶（快捷键：“F11”）"
        win_main_menu.add_cascade(label=menu_topmost_label, command=self.switch_win_topmost)
        self.config(menu=win_main_menu)

    def build_win_main_frame(self, master):
        item_width = self.gui_config.default.win_main.item.width
        item_height = self.gui_config.default.win_main.item.height
        fg_color = self.gui_config.default.win_main.item.fg_color
        bg_color = self.gui_config.default.win_main.item.bg_color
        num_one_line = self.gui_config.default.win_main.x // self.gui_config.default.win_main.item.width
        i = -1
        for character_name in self.characters:
            i += 1
            # 坐标计算
            x = i // num_one_line
            y = i % num_one_line
            item_frame = tk.Frame(
                master,
                width=item_width,
                height=item_height,
                bg=bg_color
            )
            item_frame.grid_propagate(0)
            item_frame.grid(
                row=x,
                column=y,
            )
            state = tk.BooleanVar()
            character_check_button = tk.Checkbutton(
                item_frame,
                text=character_name.split(" ").pop().split("·").pop().ljust(5, chr(12288)),
                fg=fg_color,
                bg=bg_color,
                selectcolor=bg_color,
                variable=state,
                command=lambda target_character=self.characters[character_name],
                               character_state=state: self.trigger_character_button(target_character, character_state)
            )
            character_check_button.grid(
                row=1,
                column=1,
            )
            character_check_button.state = state
            self.character_check_button[character_name] = character_check_button
            character_img_item = tk.Label(
                item_frame,
                bg="black",
                image=self.head_img[character_name],
                borderwidth=0,
                relief='ridge',
            )
            character_img_item.grid(
                row=2,
                column=1,
                sticky="W",
            )

            def enter_character_img(event, target_character_name=character_name):
                self.show_character_info(target_character_name)

            def leave_character_img(event):
                self.hide_win(self.win_character_info)

            character_img_item.bind("<Enter>", enter_character_img)
            character_img_item.bind("<Leave>", leave_character_img)

    def build_win_temporary_strategy(self):
        self.win_temporary_strategy.overrideredirect(True)
        self.win_temporary_strategy.attributes(
            "-alpha", self.gui_config.default.win_temporary_strategy.alpha)
        # 窗口大小
        width = self.gui_config.default.win_temporary_strategy.width
        height = self.gui_config.default.win_temporary_strategy.height
        # 标题栏大小
        title_width = self.gui_config.default.win_temporary_strategy.title.width
        title_height = self.gui_config.default.win_temporary_strategy.title.height
        # 背景色和前景色
        bg = self.gui_config.default.win_temporary_strategy.title.bg.passive
        fg = self.gui_config.default.win_temporary_strategy.title.fg
        # 窗口大小
        g_conf = str(width) + "x" + str(height)
        self.win_temporary_strategy.geometry(g_conf)
        # 窗口偏移
        g_conf = "+" + str(self.gui_config.default.win_temporary_strategy.migration.x) + \
                 "+" + str(self.gui_config.default.win_temporary_strategy.migration.y)
        self.win_temporary_strategy.geometry(g_conf)
        self.win_temporary_strategy.resizable(width=False, height=False)
        self.win_temporary_strategy.grid_propagate(0)
        self.win_temporary_strategy.grid()

        container_frame = tk.Frame(
            self.win_temporary_strategy,
            bg=bg,
            width=width,
            height=height,
            padx=self.gui_config.default.win_temporary_strategy.padx,
            pady=self.gui_config.default.win_temporary_strategy.pady
        )
        container_frame.grid_propagate(0)
        container_frame.grid()
        title_frame = tk.Frame(
            container_frame,
            width=width,
            height=title_height,
            bg=bg
        )
        title_frame.grid_propagate(0)
        title_frame.grid(
            sticky="W"
        )
        title1 = tk.Button(
            title_frame,
            text="前期阵容",
            bg=bg,
            fg=fg,
            command=lambda title_name="early_lineup": self.click_strategy_frame_title(title_name)
        )
        title1.grid(row=0, column=0)
        self.win_temporary_strategy_titles["early_lineup"] = title1
        title2 = tk.Button(
            title_frame,
            text="中期阵容",
            bg=bg,
            fg=fg,
            command=lambda title_name="mid_term_lineup": self.click_strategy_frame_title(title_name)
        )
        self.win_temporary_strategy_titles["mid_term_lineup"] = title2
        title2.grid(row=0, column=1)
        title3 = tk.Button(
            title_frame,
            text="后期阵容",
            bg=bg,
            fg=fg,
            command=lambda title_name="final_lineup": self.click_strategy_frame_title(title_name)
        )
        title3.grid(row=0, column=2)
        self.win_temporary_strategy_titles["final_lineup"] = title3
        title4 = tk.Button(
            title_frame,
            text="运营思路",
            bg=bg,
            fg=fg,
            command=lambda title_name="thinking": self.click_strategy_frame_title(title_name)
        )
        title4.grid(row=0, column=3)
        self.win_temporary_strategy_titles["thinking"] = title4
        # 前期阵容窗口
        early_lineup_frame = ScrollableFrame(
            container_frame,
            width=width,
            height=height,
            highlightthickness=0,
            bg=bg
        )
        # 中期阵容窗口
        mid_term_lineup_frame = ScrollableFrame(
            container_frame,
            width=width,
            height=height,
            highlightthickness=0,
            bg=bg
        )
        # 后期阵容窗口
        final_lineup_frame = ScrollableFrame(
            container_frame,
            width=width,
            height=height,
            highlightthickness=0,
            bg=bg
        )
        # 运营思路窗口
        thinking_frame = ScrollableFrame(
            container_frame,
            width=width,
            height=height,
            highlightthickness=0,
            bg=bg
        )
        # 运营思路文本
        thinking_text = tk.Label(
            thinking_frame.scrollable_frame,
            text="运营思路",
            bg=bg,
            fg=fg,
            font=t_font(size=15),
            wraplength=width - 10,
            justify="left"
        )
        self.after(500, thinking_text.grid)
        self.win_temporary_strategy_content_frames["early_lineup"]["main"] = early_lineup_frame
        self.win_temporary_strategy_content_frames["mid_term_lineup"]["main"] = mid_term_lineup_frame
        self.win_temporary_strategy_content_frames["final_lineup"]["main"] = final_lineup_frame
        self.win_temporary_strategy_content_frames["thinking"]["main"] = thinking_frame
        self.win_temporary_strategy_content_frames["thinking"]["main"] = thinking_frame
        self.win_temporary_strategy_content_frames["thinking"]["text"] = thinking_text

    def click_strategy_frame_title(self, target_title_name):
        bg_active = self.gui_config.default.win_temporary_strategy.title.bg.active
        bg_passive = self.gui_config.default.win_temporary_strategy.title.bg.passive
        for title_name in self.win_temporary_strategy_titles:
            if title_name == target_title_name:
                self.win_temporary_strategy_titles[title_name].config(bg=bg_active)
                if target_title_name == "thinking":
                    pass
                else:
                    self.lineup_focus = target_title_name

            else:
                self.win_temporary_strategy_titles[title_name].config(bg=bg_passive)
                self.win_temporary_strategy_content_frames[title_name]["main"].grid_forget()
        self.win_temporary_strategy_content_frames[target_title_name]["main"].grid()
        self.adapt_lineup_main()

    def adapt_lineup_main(self):
        for lineup_name in self.temporary_strategy["lineups"]:
            if lineup_name != self.lineup_focus:
                for character_name in self.temporary_strategy["lineups"][lineup_name]:
                    self.character_check_button[character_name].deselect()
        for character_name in self.temporary_strategy["lineups"][self.lineup_focus]:
            self.character_check_button[character_name].select()

    def build_win_equipment_list(self):

        self.win_equipment_list.overrideredirect(True)
        self.win_equipment_list.attributes('-topmost', True)
        self.win_equipment_list.attributes(
            "-alpha", self.gui_config.default.win_equipments_list.alpha)
        # 窗口大小
        win_equipments_list_width = self.gui_config.default.win_equipments_list.width
        win_equipments_list_height = self.gui_config.default.win_equipments_list.height
        g_conf = str(win_equipments_list_width) + "x" + str(win_equipments_list_height)
        self.win_equipment_list.geometry(g_conf)
        self.win_equipment_list.resizable(width=False, height=False)
        bg = self.gui_config.default.win_equipments_list.bg_color.default
        self.win_equipment_list_frame = tk.Frame(
            self.win_equipment_list,
            bg=bg,
            width=win_equipments_list_width,
            height=win_equipments_list_height
        )
        self.win_equipment_list_frame.grid_propagate(0)
        self.win_equipment_list_frame.grid()
        num_one_line = self.gui_config.default.win_equipments_list.max_x_num
        i = -1
        default_equipment_name = self.gui_config.default.win_equipments_list.equipment.name_default
        for equipment_name in self.equipments:
            if not self.equipments[equipment_name].type == \
                   self.gui_config.default.win_equipments_list.equipment.type.combination:
                continue
            i += 1
            x = i // num_one_line
            y = i % num_one_line
            if x == 0 and y == 0:
                equipment_name = default_equipment_name
            else:
                if equipment_name == default_equipment_name:
                    continue
            equipment_button = tk.Button(
                self.win_equipment_list_frame,
                image=self.equipment_img[equipment_name],
                bg=bg
            )
            equipment_button.grid(
                row=x,
                column=y
            )

            def enter_equipment_button(event, c_equipment_name=equipment_name):
                self.show_equipment_info(c_equipment_name)

            # def leave_equipment_button(event):
            #     pass

            def click_equipment_button(event, new_equipment_name=equipment_name):
                self.replace_equipment(event, new_equipment_name)
                self.hide_win(self.win_equipment_list)
                self.hide_win(self.win_equipment_info)

            equipment_button.bind("<ButtonRelease-1>", click_equipment_button)
            equipment_button.bind("<Enter>", enter_equipment_button)

        def cursor_leave(event):
            self.cursor_if_leave_then_hide(event, self.win_equipment_list)
            self.hide_win(self.win_equipment_info)

        self.win_equipment_list.bind("<Leave>", cursor_leave)

    def build_win_equipment_info(self):
        self.win_equipment_info.overrideredirect(True)
        self.win_equipment_info.attributes('-topmost', True)
        self.win_equipment_info.attributes(
            "-alpha", self.gui_config.default.win_equipments_list.alpha)
        # gui设置
        win_equipments_info_width = self.gui_config.default.win_equipment_info.width
        win_equipments_info_height = self.gui_config.default.win_equipment_info.height
        # 分隔栏
        win_line_span_height = self.gui_config.default.win_equipment_info.line_span.height
        win_line_span_color = self.gui_config.default.win_equipment_info.line_span.color
        # 主背景色和字体颜色
        bg = self.gui_config.default.win_equipment_info.fg
        fg = self.gui_config.default.win_equipment_info.bg
        # 装备姓名栏宽高
        win_equipment_name_width = win_equipments_info_width
        win_equipment_name_height = win_equipments_info_height / 7
        # 基础装备栏宽高
        win_f_equip_width = win_equipments_info_width / 2
        win_f_equip_height = win_equipments_info_height / 3.5
        # 装备技能栏宽高
        win_equip_skill_width = win_equipments_info_width
        win_equip_skill_height = win_equipments_info_height \
                                 - win_equipment_name_height \
                                 - win_line_span_height \
                                 - win_f_equip_height \
                                 - win_line_span_height

        default_equipment_name = self.gui_config.default.win_temporary_strategy.item.equipment.name_default
        g_conf = str(win_equipments_info_width) + "x" + str(win_equipments_info_height)

        self.win_equipment_info.geometry(g_conf)
        self.win_equipment_info.resizable(width=False, height=False)

        win_equipment_out_line_frame = tk.Frame(
            self.win_equipment_info,
            bg=bg,
            width=win_equipments_info_width,
            height=win_equipments_info_height
        )
        win_equipment_out_line_frame.grid_propagate(0)
        win_equipment_out_line_frame.grid()
        win_equipment_title_frame = tk.Frame(
            master=win_equipment_out_line_frame,
            bg=bg,
            width=win_equipment_name_width,
            height=win_equipment_name_height
        )
        win_equipment_title_frame.grid_propagate(0)
        win_equipment_title_frame.grid(
            row=0,
            column=0,
            columnspan=2,
        )
        win_equipment_img = tk.Label(
            win_equipment_title_frame,
            image=self.equipment_img[default_equipment_name],
            fg=fg,
            bg=bg
        )
        win_equipment_img.grid(
            row=0,
            column=0
        )
        win_equipment_name = tk.Label(
            win_equipment_title_frame,
            text=default_equipment_name,
            fg=fg,
            bg=bg
        )
        win_equipment_name.grid(
            row=0,
            column=1
        )
        # 分隔栏
        tk.Frame(
            master=win_equipment_out_line_frame,
            bg=win_line_span_color,
            width=win_equipments_info_width,
            height=win_line_span_height
        ).grid(
            row=1,
            column=0,
            columnspan=2
        )

        # 左边基础装备栏
        win_equipment_left_frame = tk.Frame(
            master=win_equipment_out_line_frame,
            bg=bg,
            width=win_f_equip_width,
            height=win_f_equip_height
        )
        win_equipment_left_frame.grid_propagate(0)
        win_equipment_left_frame.grid(
            row=2,
            column=0,
            columnspan=1
        )
        win_equipment_left_title_img = tk.Label(
            win_equipment_left_frame,
            image=self.equipment_img[default_equipment_name],
            bg=bg
        )
        win_equipment_left_title_img.grid(
            row=0,
            column=0, )
        win_equipment_left_title_name = tk.Label(
            win_equipment_left_frame,
            text="",
            fg=fg,
            bg=bg
        )
        win_equipment_left_title_name.grid(
            row=0,
            column=1,
        )
        win_equipment_left_content_text = tk.Label(
            win_equipment_left_frame,
            text="",
            fg=fg,
            bg=bg,
            wraplength=win_f_equip_width - 5,
            justify='left',
        )
        # statistics
        win_equipment_left_content_text.grid(
            row=1,
            column=0,
            columnspan=2
        )
        win_equipment_right_frame = tk.Frame(
            master=win_equipment_out_line_frame,
            bg=bg,
            width=win_f_equip_width,
            height=win_f_equip_height
        )
        win_equipment_right_frame.grid_propagate(0)
        win_equipment_right_frame.grid(
            row=2,
            column=1,
            columnspan=1
        )
        win_equipment_right_title_img = tk.Label(
            win_equipment_right_frame,
            image=self.equipment_img[default_equipment_name],
            bg=bg
        )
        win_equipment_right_title_img.grid(
            row=0,
            column=0,
        )
        win_equipment_right_title_name = tk.Label(
            win_equipment_right_frame,
            text="",
            fg=fg,
            bg=bg
        )
        win_equipment_right_title_name.grid(
            row=0,
            column=1,
        )
        # statistics
        win_equipment_right_content_text = tk.Label(
            win_equipment_right_frame,
            text="",
            fg=fg,
            bg=bg,
            wraplength=win_f_equip_width - 5,
            justify='left',
        )
        win_equipment_right_content_text.grid(
            row=1,
            column=0,
            columnspan=2
        )
        # 分隔栏
        tk.Frame(
            master=win_equipment_out_line_frame,
            bg=win_line_span_color,
            width=win_equipments_info_width,
            height=win_line_span_height
        ).grid(
            row=3,
            column=0,
            columnspan=2
        )
        # 技能说明栏
        win_equipment_skill_frame = tk.Frame(
            master=win_equipment_out_line_frame,
            bg=bg,
            width=win_equip_skill_width,
            height=win_equip_skill_height
        )
        win_equipment_skill_frame.grid(
            row=4,
            column=0,
            columnspan=2
        )
        win_equipment_skill_frame.grid_propagate(0)
        win_equipment_skill_text = tk.Label(
            win_equipment_skill_frame,
            text="",
            fg=fg,
            bg=bg,
            wraplength=win_equip_skill_width - 5,
            justify='left',
        )
        win_equipment_skill_text.grid()
        self.win_equipment_info_frame = {
            "combination": {
                "img": win_equipment_img,
                "name": win_equipment_name,
                "skill": win_equipment_skill_text
            },
            "foundation": [
                {
                    "img": win_equipment_left_title_img,
                    "name": win_equipment_left_title_name,
                    "statistics": win_equipment_left_content_text
                },
                {
                    "img": win_equipment_right_title_img,
                    "name": win_equipment_right_title_name,
                    "statistics": win_equipment_right_content_text
                },
            ]
        }
        #

    def build_win_character_info(self):
        # self.show_win(self.win_character_info)
        self.win_character_info.overrideredirect(True)
        self.win_character_info.attributes('-topmost', True)
        self.win_character_info.attributes(
            "-alpha", self.gui_config.default.win_equipments_list.alpha)
        # gui设置
        # 窗口宽高
        win_character_info_width = self.gui_config.default.win_character_info.width
        win_character_info_height = self.gui_config.default.win_character_info.height
        # 分隔栏
        win_line_span_height = self.gui_config.default.win_character_info.line_span.height
        win_line_span_color = self.gui_config.default.win_character_info.line_span.color
        # 主背景色和字体颜色
        bg = self.gui_config.default.win_equipment_info.fg
        fg = self.gui_config.default.win_equipment_info.bg
        # 标题栏宽高
        win_character_title_width = self.gui_config.default.win_character_info.title.width
        win_character_title_height = self.gui_config.default.win_character_info.title.height
        # 费用栏宽高
        win_character_cost_width = self.gui_config.default.win_character_info.cost.width
        win_character_cost_height = self.gui_config.default.win_character_info.cost.height
        # 技能栏
        # 费用栏
        # 属性栏
        win_character_info_scroll_frame_height = win_character_info_height \
                                                 - win_character_title_height \
                                                 - win_line_span_height \
                                                 - win_character_cost_height
        default_equipment_name = self.gui_config.default.win_temporary_strategy.item.equipment.name_default
        win_character_out_line_frame = tk.Frame(
            self.win_character_info,
            bg=bg,
            width=win_character_info_width,
        )
        # win_character_out_line_frame.grid_propagate(0)
        win_character_out_line_frame.grid()
        # 标题栏 含有英雄头像和姓名
        win_character_title_frame = tk.Frame(
            master=win_character_out_line_frame,
            bg=bg,
            width=win_character_title_width,
            height=win_character_title_height
        )
        win_character_title_frame.grid(
            row=0,
            column=0,
            sticky="W"
        )
        win_character_head_img = tk.Label(
            win_character_title_frame,
            image=self.equipment_img[default_equipment_name],
            fg=fg,
            bg=bg
        )
        win_character_head_img.grid(
            row=0,
            column=0,
            sticky="W"
        )
        win_character_name = tk.Label(
            win_character_title_frame,
            text=default_equipment_name,
            fg=fg,
            bg=bg
        )
        win_character_name.grid(
            row=0,
            column=1,
            sticky="W"
        )
        # 分隔栏
        tk.Frame(
            master=win_character_out_line_frame,
            bg=win_line_span_color,
            width=win_character_info_width,
            height=win_line_span_height
        ).grid(
            row=1,
            column=0,
            sticky='W'
        )
        # 英雄费用栏
        win_character_cost_frame = tk.Frame(
            master=win_character_out_line_frame,
            bg=bg,
            width=win_character_cost_width,
            height=win_character_cost_height
        )
        # win_character_cost_frame.grid_propagate(False)
        win_character_cost_frame.grid(
            row=2,
            column=0,
            sticky="W"
        )
        # 费用
        tk.Label(
            master=win_character_cost_frame,
            text="费用:",
            # font=tf.Font(weight="bold"),
            bg=bg,
            fg=fg,
        ).grid(
            row=0,
            column=0,
            sticky='W'
        )
        win_character_cost_text = tk.Label(
            master=win_character_cost_frame,
            text="0",
            bg=bg,
            fg=fg,
        )
        win_character_cost_text.grid(
            row=0,
            column=1,
            sticky='W'
        )
        # 分隔栏
        tk.Frame(
            master=win_character_out_line_frame,
            bg=win_line_span_color,
            width=win_character_info_width,
            height=win_line_span_height
        ).grid(
            row=3,
            column=0,
            sticky='W'
        )
        # 英雄羁绊标题
        tk.Label(
            master=win_character_out_line_frame,
            text="羁绊：",
            wraplength=win_character_info_width - 5,
            justify='left',
            bg=bg,
            fg=fg,
        ).grid(
            row=4,
            column=0,
            sticky='W'
        )
        # 英雄羁绊文本
        win_character_status_text = tk.Label(
            master=win_character_out_line_frame,
            text="未初始化",
            wraplength=win_character_info_width - 5,
            justify='left',
            bg=bg,
            fg=fg,
        )
        win_character_status_text.grid(
            row=5,
            column=0,
            sticky='W'
        )
        # 分隔栏
        tk.Frame(
            master=win_character_out_line_frame,
            bg=win_line_span_color,
            width=win_character_info_width,
            height=win_line_span_height
        ).grid(
            row=6,
            column=0,
            sticky='W'
        )
        # 滚动窗口
        win_skill_sta_con_frame = tk.Frame(
            win_character_out_line_frame,
            bg=bg,
            width=100
        )
        win_skill_sta_con_frame.grid(
            row=7,
            column=0,
            sticky='W'
        )
        # 英雄技能标题
        tk.Label(
            master=win_skill_sta_con_frame,
            text="技能：",
            wraplength=win_character_info_width - 5,
            justify='left',
            bg=bg,
            fg=fg,
        ).grid(
            sticky='W'
        )
        # 英雄技能文本
        win_character_skill_text = tk.Label(
            master=win_skill_sta_con_frame,
            text="未初始化",
            wraplength=win_character_info_width - 5,
            justify='left',
            bg=bg,
            fg=fg,
        )
        win_character_skill_text.grid(
            sticky='W'
        )
        # 分隔栏
        tk.Frame(
            master=win_skill_sta_con_frame,
            bg=win_line_span_color,
            width=win_character_info_width,
            height=win_line_span_height
        ).grid()
        # 英雄属性标题
        tk.Label(
            master=win_skill_sta_con_frame,
            text="属性：",
            wraplength=win_character_info_width - 5,
            justify='left',
            bg=bg,
            fg=fg,
        ).grid(
            sticky='W'
        )
        # 英雄属性标题
        win_character_sta_text = tk.Label(
            master=win_skill_sta_con_frame,
            text="未初始化",
            wraplength=win_character_info_width - 5,
            justify='left',
            bg=bg,
            fg=fg,
        )
        win_character_sta_text.grid(
            sticky='W'
        )
        self.win_character_info_frame = {
            "character_head_img": win_character_head_img,
            "character_name": win_character_name,
            "character_cost": win_character_cost_text,
            "character_status": win_character_status_text,
            "character_skill": win_character_skill_text,
            "character_statistics": win_character_sta_text,
        }

    def show_character_info(self, character_name):
        x, y = get_cursor_pos()
        character = self.characters[character_name]
        self.win_character_info_frame["character_head_img"].configure(image=self.head_img[character_name])
        self.win_character_info_frame["character_name"].configure(text=character.name)
        self.win_character_info_frame["character_cost"].configure(text=character.price)
        status_line = character.status[0]
        for status in character.status[1:]:
            status_line = "{}、{}".format(status_line, status)
        self.win_character_info_frame["character_status"].configure(text=status_line)
        self.win_character_info_frame["character_skill"].configure(text="".join(character.skill.split()))
        sta_line = ""
        for k, v in character.statistics.items():
            if sta_line == "":
                sta_line = "{}：{}".format(k, "/".join(v))
            else:
                sta_line = "{}\n{}：{}".format(sta_line, k, "/".join(v))
        self.win_character_info_frame["character_statistics"].configure(text=sta_line)
        self.show_win(self.win_character_info, (x + 30, y + 30))

    def show_equipment_info(self, equipment_name):
        x, y = get_cursor_pos()
        equipment = self.equipments[equipment_name]
        self.win_equipment_info_frame["combination"]["name"].configure(text=equipment_name)
        self.win_equipment_info_frame["combination"]["img"].configure(image=self.equipment_img[equipment_name])
        self.win_equipment_info_frame["combination"]["skill"].configure(text=equipment.skill)
        if not isinstance(equipment.components, list):
            return False
        else:
            i = -1
            for component_name in equipment.components:
                i += 1
                self.win_equipment_info_frame["foundation"][i]["name"].configure(text=component_name)
                self.win_equipment_info_frame["foundation"][i]["img"] \
                    .configure(image=self.equipment_img[component_name])
                self.win_equipment_info_frame["foundation"][i]["statistics"] \
                    .configure(text="".join(self.equipments[component_name].statistics))
        self.show_win(self.win_equipment_info, (x + 50, y + 50))

    def refresh_thinking_text(self):
        return

    def add_lineup_frame_item(self, lineup_name, character_name):
        item_width = self.gui_config.default.win_temporary_strategy.item.width
        item_height = self.gui_config.default.win_temporary_strategy.item.height
        bg_color = self.gui_config.default.win_temporary_strategy.item.bg_color
        fg_color = self.gui_config.default.win_temporary_strategy.item.fg_color
        # text_max_len = self.gui_config.default.win_temporary_strategy.item.text.max_len

        # 角色渲染区,当需要删除角色渲染时,删除item_frame,item_frame.destroy()
        item_frame = tk.Frame(
            self.win_temporary_strategy_content_frames[lineup_name]["main"].scrollable_frame,
            width=item_width,
            height=item_height,
            bg=bg_color
        )
        character = self.characters[character_name]
        self.win_temporary_strategy_content_frames[lineup_name]["items"][character.name] = item_frame
        item_frame.grid_propagate(0)
        item_frame.grid(pady=1)
        # 渲染坐标
        y = len(self.temporary_strategy["lineups"][lineup_name])
        # 角色名
        state = tk.BooleanVar()
        ally_button = tk.Checkbutton(
            item_frame,
            text=character.name.split(" ").pop().split("·").pop().ljust(5, chr(12288)),
            selectcolor=self.gui_config.default.win_main.item.bg_color,
            bg=bg_color,
            fg=fg_color,
            command=lambda button_state=state: self.trigger_ally_button(character, state),
            variable=state
        )
        ally_button.grid(
            row=0,
            column=y
        )
        state.set(True)
        # 角色相片
        character_img_item = tk.Label(
            item_frame,
            image=self.head_img[character.name],
            bg=bg_color,
            fg=fg_color
        )
        character_img_item.grid(
            row=0,
            column=y + 1
        )

        def enter_character_img(event, target_character_name=character.name):
            self.show_character_info(target_character_name)

        def leave_character_img(event):
            self.hide_win(self.win_character_info)

        character_img_item.bind("<Enter>", enter_character_img)
        character_img_item.bind("<Leave>", leave_character_img)

        # 角色装备
        equipment_image_width = self.gui_config.default.win_temporary_strategy.item.equipment.image.width
        equipment_image_height = self.gui_config.default.win_temporary_strategy.item.equipment.image.height
        equipment_max_num = self.gui_config.default.win_temporary_strategy.item.equipment.max_num
        default_equipment_name = self.gui_config.default.win_temporary_strategy.item.equipment.name_default
        ally = self.temporary_strategy["lineups"][lineup_name].get(character_name, False)
        logger.debug(ally)
        logger.debug(not ally)
        if not ally:
            return
        for i in range(equipment_max_num):
            if not ally.equipment or not isinstance(ally.equipment, list):
                equipment_name = default_equipment_name
            else:
                num_ally_equipment = len(ally.equipment)
                if i < num_ally_equipment:
                    equipment_name = ally.equipment[i]
                else:
                    equipment_name = default_equipment_name
            equipment_img = self.equipment_img[equipment_name]
            equipment_button = tk.Button(
                item_frame,
                image=equipment_img,
                width=equipment_image_width,
                height=equipment_image_height,
                bg=bg_color,
            )
            equipment_button.grid(
                row=0,
                column=y + 2 + i
            )

            def replace_equipment(event, equipment_item=equipment_button, character_name=ally.character, loc=i):
                return self.replace_equipment_start(equipment_item, character_name, loc)

            equipment_button.bind("<Button-1>", replace_equipment)
        # self.show_win(self.win_equipment_list)

    def replace_equipment_start(self, equipment_item, character_name, loc):
        x, y = get_cursor_pos()
        self.win_equipment_list.geometry("+{}+{}".format(x - 1, y - 1))
        self.focus_ally = {
            "equipment_button": equipment_item,
            "character_name": character_name,
            "equipment_loc": loc
        }
        self.show_win_equipment_list()

    def remove_win_temporary_strategy_item(self, character):
        logger.debug(self.lineup_focus)
        self.win_temporary_strategy_content_frames[self.lineup_focus]["items"][character.name].destroy()

    def cursor_if_leave_then_hide(self, event, win):
        if event.widget != win:
            return
        self.hide_win(win)

    def replace_equipment(self, event, new_equipment_name):
        # 默认装备
        default_equipment_name = self.gui_config.default.win_temporary_strategy.item.equipment.name_default
        # 人物名
        character_name = self.focus_ally["character_name"]
        # 第几个装备
        equipment_loc = self.focus_ally["equipment_loc"]
        ally = self.final_lineup_allys[character_name]
        ally_equipment_data = [default_equipment_name] * 3
        if not ally.equipment or not isinstance(ally.equipment, list):
            logger.warning("警告，数据异常，当前装备数据异常，重新初始化，装备数据:{}".format(ally.equipment))
        elif len(ally.equipment) < 3:
            i = 0
            for equipment_name in ally.equipment:
                ally_equipment_data[i] = equipment_name
        elif len(ally.equipment) == 3:
            ally_equipment_data = ally.equipment
        else:
            logger.error("错误，数据异常，当前装备数量异常，装备数据:{}".format(ally.equipment))
        if ally_equipment_data[equipment_loc] == new_equipment_name:
            return True
        ally_equipment_data[equipment_loc] = new_equipment_name
        new_ally = lineup_controller.update_lineup_ally(self.final_lineup_index, ally.character,
                                                        {"equipment": ally_equipment_data})
        self.final_lineup_allys[character_name] = new_ally
        target_equipment_button = self.focus_ally["equipment_button"]
        target_equipment_button.configure(image=self.equipment_img[new_equipment_name])

    def show_win_equipment_list(self):
        x, y = get_cursor_pos()
        self.show_win(self.win_equipment_list, (x - 1, y - 1))

    @staticmethod
    def show_win(win, migration=None):
        if migration:
            g_conf = "+{}+{}".format(migration[0], migration[1])
            win.geometry(g_conf)
        win.deiconify()

    @staticmethod
    def hide_win(win):
        win.withdraw()

    def select_all(self):
        if self.tk.call('after', 'info'):
            logger.warning("中止，正在执行其他的批量任务")
            return
        try:
            i = 0
            for character_name in self.characters:
                i += 1
                if character_name in self.final_lineup_allys:
                    continue
                else:
                    self.after(10 * i, lambda name=character_name: self.character_check_button[
                        name].invoke())
        except:
            logger.critical("错误，批量任务执行失败，任务:select_all")

    def reject_all(self):
        if self.tk.call('after', 'info'):
            logger.warning("中止，正在执行其他的批量任务")
            return
        try:
            character_list = list(self.final_lineup_allys.keys())
            character_list.reverse()
            i = 0
            for character_name in character_list:
                i += 1
                self.after(10 * i, lambda name=character_name: self.character_check_button[
                    name].invoke())
        except:
            logger.critical("错误，批量任务执行失败，任务:reject_all")

    def switch_win_topmost(self):
        self.is_win_topmost = not self.is_win_topmost
        if self.is_win_topmost:
            self.lift()
            self.attributes('-topmost', True)
            self.win_temporary_strategy.lift()
            self.win_temporary_strategy.attributes('-topmost', True)
        else:
            self.attributes('-topmost', False)
            self.win_temporary_strategy.attributes('-topmost', False)
        self.build_win_main_menu()

    def active(self):
        self.state = 1
        title_text = self.gui_config.default.win_main.title.text.positive
        self.set_state_then_title(title_text)

    def deactivate(self):
        self.state = 0
        title_text = self.gui_config.default.win_main.title.text.negative
        self.set_state_then_title(title_text)

    def change_state_then_title(self):
        self.state = 1 - self.state
        if self.state:
            self.active()
        else:
            self.deactivate()

    def set_state_then_title(self, title_text):
        try:
            set_state(self.state)
            self.title(title_text)
        except:
            logger.critical("状态设置失败，未知的原因，当前状态:{}".format(self.state))

    def refresh_strategy(self):
        self.build_win_main_menu()

    def import_strategy_from_name(self, name):
        pass

    def import_strategy_from_file(self, file_path=""):
        pass

    def export_strategy(self):
        pass

    # 键盘事件开始
    def listenKeyboard(self):
        def ifDel():
            hm = PyHook3.HookManager()
            hm.KeyDown = self.keyBoardEvent
            hm.HookKeyboard()
            pythoncom.PumpMessages()

        t1 = Thread(target=ifDel)
        t1.setDaemon(True)
        t1.start()

    def keyBoardEvent(self, key):
        if str(key) == 'Key.f8':
            self.change_state_then_title()
        if str(key) == 'Key.f9':
            self.reject_all()
        if str(key) == 'Key.f10':
            self.trigger_character_button_all()
        if str(key) == 'Key.f11':
            self.top_down()

    # 键盘事件结束
    def select_character_to_lineup(self, character):
        lineup_index = self.lineup_index[self.lineup_focus]
        ally = self.lineup_get_ally(lineup_index, character)
        self.temporary_strategy["lineups"][self.lineup_focus][character.name] = ally
        self.add_lineup_frame_item(self.lineup_focus, ally.character)
        self.character_check_button[character.name].state.set(True)

    def reject_character_from_lineup(self, character):
        lineup_index = self.lineup_index[self.lineup_focus]
        logger.info("执行中,尝试从阵容中删除角色,阵容索引:{}，角色:{}".format(lineup_index, character))
        ally_name = lineup_controller.lose_ally(lineup_index, character.name)
        if not ally_name:
            logger.critical("错误，无法移除角色，表索引:{}，目标角色:{}".format(lineup_index, character))
            return
        del self.temporary_strategy["lineups"][self.lineup_focus][ally_name]
        self.remove_win_temporary_strategy_item(character)

    def trigger_ally_button(self, character, state):
        self.reject_character_from_lineup(character)
        if character.name in self.character_check_button:
            self.character_check_button[character.name].deselect()

    def trigger_character_button(self, character, character_state):
        accept_character = character_state.get()
        character_in_lineup = 0
        if character.name in self.temporary_strategy["lineups"][self.lineup_focus]:
            character_in_lineup = 1
        if accept_character and not character_in_lineup:
            self.select_character_to_lineup(character)
        if not accept_character and character_in_lineup:
            self.reject_character_from_lineup(character)
