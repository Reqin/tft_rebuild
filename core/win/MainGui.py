# coding:utf8
import os
import time
import tkinter as tk
import tkinter.messagebox as msgBox
import requests
from PIL import ImageTk, Image
from threading import Thread
from core.state.state import set_state, set_lineup_state
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
import win32api, win32con
from core.filePipe.pipe import read_all
import keyboard


def start_main_window():
    main_win = MainGui()
    main_win.mainloop()


def t_font(family="", **kwargs):
    return tf.Font(family=family, **kwargs)


class MainGui(tk.Tk):
    def __init__(self):
        super().__init__()
        # 设置状态
        set_state(0)
        # 加载配置文件
        self.gui_config = config_parser(config_init.user.path).gui
        # 初始化资源
        # cache some
        self.cache_some = []
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
        self.hide_win(self)
        # 主窗口所有角色按钮
        self.character_check_button = dict()
        # 当前阵容窗口
        self.win_temporary_strategy = tk.Toplevel()
        self.hide_win(self.win_temporary_strategy)
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
        # 生成策略时询问策略名称窗口
        self.win_new_strategy_name = tk.Toplevel()
        self.hide_win(self.win_new_strategy_name)
        # 生成阵容名称输入框
        self.win_new_strategy_name_entry = None
        # 在lineup中最近一次点击的ally元素，其中包含character.name和equipment_button
        self.focus_ally = dict()
        # 窗口是否置顶
        self.top = False
        # 用于判断是否激活主窗口
        self.is_active = True
        # 用于判断当前窗口是否置顶
        self.is_win_topmost = False
        self.build()
        # 认证窗口
        self.win_auth = tk.Toplevel()
        self.hide_win(self.win_auth)
        self.after(5, self.auth)

    def auth_success(self):
        self.win_auth.destroy()
        # 激活主窗口
        self.active()
        # 显示主窗口
        self.show_win(self)
        # 显示当前阵容窗口
        self.show_win(self.win_temporary_strategy)
        # 监听键盘
        keyboard.add_hotkey("f8", self.change_state_then_title)
        keyboard.add_hotkey("f11", self.switch_win_topmost)

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

    def load_temporary_strategy(self, name=None):
        temporary_strategy_name = component_config.temporary_strategy.major_filed_value
        temporary_strategy = strategy.get(temporary_strategy_name)
        if not temporary_strategy:
            logger.warning("执行中，默认阵容未初始化，开始初始化:{}".format(component_config.temporary_strategy.record_index))
            strategy.record({strategy.major_field: component_config.temporary_strategy.major_filed_value})
            self.load_temporary_strategy()
        if name and (new_temporary_strategy := strategy.get(name)):
            strategy.copy_strategy(new_temporary_strategy, temporary_strategy)
            strategy.update({"thinking": new_temporary_strategy.thinking}, temporary_strategy_name)
            temporary_strategy = strategy.get(temporary_strategy_name)
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

    def destroy_temporary_strategy_items(self):
        for item in self.win_temporary_strategy_content_frames["early_lineup"]["items"].values():
            item.destroy()
        for item in self.win_temporary_strategy_content_frames["mid_term_lineup"]["items"].values():
            item.destroy()
        for item in self.win_temporary_strategy_content_frames["final_lineup"]["items"].values():
            item.destroy()
        self.win_temporary_strategy_content_frames["thinking"]["text"].destroy()

    def build_strategy_items(self):
        self.build_lineups_frame()
        self.build_thinking_text_frame()

    def build_lineups_frame(self):
        for lineup_name in self.temporary_strategy["lineups"]:
            self.build_lineup_frame(lineup_name)

    def build_lineup_frame(self, lineup_name):
        for name in self.temporary_strategy["lineups"][lineup_name]:
            self.character_check_button[name].state.set(True)
            self.add_lineup_frame_item(lineup_name, name)

    def build_thinking_text_frame(self):
        thinking_frame = self.win_temporary_strategy_content_frames["thinking"]["main"]
        # 窗口大小
        width = self.gui_config.default.win_temporary_strategy.width
        # 背景色和前景色
        bg = self.gui_config.default.win_temporary_strategy.title.bg.passive
        fg = self.gui_config.default.win_temporary_strategy.title.fg
        # 运营思路文本
        thinking_text = tk.Label(
            thinking_frame,
            text=self.temporary_strategy["thinking"],
            bg=bg,
            fg=fg,
            font=t_font(size=15),
            wraplength=width - 10,
            justify="left"
        )
        thinking_text.after(500, thinking_text.grid)
        self.win_temporary_strategy_content_frames["thinking"]["text"] = thinking_text

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
        item_frame_width = self.gui_config.default.win_main.item.width
        pad_x = (width % item_frame_width) // 2
        bg_frame = tk.Frame(self,
                            bg=self.gui_config.default.win_main.bg_color.default,
                            width=self.gui_config.default.win_main.x,
                            height=self.gui_config.default.win_main.y)
        bg_frame.grid_propagate(0)
        bg_frame.grid(
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )
        main_frame = tk.Frame(bg_frame,
                              bg=self.gui_config.default.win_main.bg_color.default,
                              width=width,
                              height=height)
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
        win_main_menu.add_cascade(
            label="全部取消", command=lambda: self.reject_all())
        # 自定义阵容
        strategy_menu = tk.Menu(win_main_menu, tearoff=0)
        win_main_menu.add_cascade(label="自定义阵容", menu=strategy_menu)
        strategy_menu.add_command(label='生成阵容', command=self.generate_strategy)
        # strategy_menu.add_command(label='生成阵容', command=self.import_strategy)
        # strategy_menu.add_command(label='导出', command=self.export_strategy)
        # strategy_menu.add_command(label='刷新', command=self.refresh_strategy)
        strategy_menu.add_separator()
        strategies = strategy.all()
        for one_strategy in strategies:
            if one_strategy.name == "默认":
                continue
            strategy_menu.add_command(
                label=one_strategy.name, command=lambda name=one_strategy.name: self.import_strategy_from_name(name))
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
                bg=bg_color,
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

        outline_frame = tk.Frame(
            self.win_temporary_strategy,
            bg=bg,
            width=width,
            height=height,
            padx=self.gui_config.default.win_temporary_strategy.padx,
            pady=self.gui_config.default.win_temporary_strategy.pady
        )
        outline_frame.grid_propagate(0)
        outline_frame.grid()
        title_frame = tk.Frame(
            outline_frame,
            width=title_width,
            height=title_height,
            bg=bg
        )
        title_frame.grid_propagate(0)
        title_frame.grid(
            row=0,
            column=0,
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
        # 滚动容器窗口
        e_container_frame = ScrollableFrame(
            outline_frame,
            highlightthickness=0,
            width=width,
            height=height,
            bg=bg
        )
        e_container_frame.grid_propagate(0)
        e_container_frame.grid(
            row=1,
            column=0,
            sticky="W"
        )
        # 前期阵容窗口
        early_lineup_frame = tk.Frame(
            e_container_frame.scrollable_frame,
            width=width,
            height=height,
            bg=bg
        )
        early_lineup_frame.grid()
        # 滚动容器窗口
        m_container_frame = ScrollableFrame(
            outline_frame,
            highlightthickness=0,
            width=width,
            height=height,
            bg=bg
        )
        m_container_frame.grid_propagate(0)
        m_container_frame.grid(
            row=1,
            column=0,
            sticky="W"
        )
        # 中期阵容窗口
        mid_term_lineup_frame = tk.Frame(
            m_container_frame.scrollable_frame,
            width=width,
            height=height,
            highlightthickness=0,
            bg=bg
        )
        mid_term_lineup_frame.grid()
        # 滚动容器窗口
        f_container_frame = ScrollableFrame(
            outline_frame,
            highlightthickness=0,
            width=width,
            height=height,
            bg=bg
        )
        f_container_frame.grid_propagate(0)
        f_container_frame.grid(
            row=1,
            column=0,
            sticky="W"
        )
        # 后期阵容窗口
        final_lineup_frame = tk.Frame(
            f_container_frame.scrollable_frame,
            width=width,
            height=height,
            highlightthickness=0,
            bg=bg
        )
        final_lineup_frame.grid()
        # 滚动容器窗口
        t_container_frame = ScrollableFrame(
            outline_frame,
            highlightthickness=0,
            width=width,
            height=height,
            bg=bg
        )
        t_container_frame.grid_propagate(0)
        t_container_frame.grid(
            row=1,
            column=0,
            sticky="W"
        )
        # 运营思路窗口
        thinking_frame = tk.Frame(
            t_container_frame.scrollable_frame,
            width=width,
            height=height,
            highlightthickness=0,
            bg=bg
        )
        thinking_frame.grid()
        self.win_temporary_strategy_content_frames["early_lineup"]["container"] = e_container_frame
        self.win_temporary_strategy_content_frames["mid_term_lineup"]["container"] = m_container_frame
        self.win_temporary_strategy_content_frames["final_lineup"]["container"] = f_container_frame
        self.win_temporary_strategy_content_frames["thinking"]["container"] = t_container_frame
        self.win_temporary_strategy_content_frames["early_lineup"]["main"] = early_lineup_frame
        self.win_temporary_strategy_content_frames["mid_term_lineup"]["main"] = mid_term_lineup_frame
        self.win_temporary_strategy_content_frames["final_lineup"]["main"] = final_lineup_frame
        self.win_temporary_strategy_content_frames["thinking"]["main"] = thinking_frame

    def _on_mousewheel(self, event, canvas, frame):
        height = canvas.winfo_height()
        item_height = frame.winfo_height()
        print(height, item_height)
        if (item_height < height):
            direction = 0
        else:
            direction = event.delta
        migration = int(-1 * (direction / 120))
        canvas.yview_scroll(migration, "units")

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
                    set_lineup_state(target_title_name)
            else:
                self.win_temporary_strategy_titles[title_name].config(bg=bg_passive)
                self.win_temporary_strategy_content_frames[title_name]["container"].grid_forget()
                self.win_temporary_strategy_content_frames[title_name]["container"].state = False
        self.win_temporary_strategy_content_frames[target_title_name]["container"].state = True
        self.win_temporary_strategy_content_frames[target_title_name]["container"].grid()
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
            self.win_temporary_strategy_content_frames[lineup_name]["main"],
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
        ally = self.temporary_strategy["lineups"][self.lineup_focus][character_name]
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
        new_ally = lineup_controller.update_lineup_ally(self.lineup_index[self.lineup_focus], ally.character,
                                                        {"equipment": ally_equipment_data})
        self.temporary_strategy["lineups"][self.lineup_focus][character_name] = new_ally
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
                if character_name in self.temporary_strategy["lineups"][self.lineup_focus]:
                    continue
                else:
                    self.character_check_button[character_name].invoke()
                    # self.after(20 * i, lambda name=character_name: self.character_check_button[
                    #     name].invoke())
        except:
            logger.critical("错误，批量任务执行失败，任务:select_all")

    def reject_all(self):
        if self.tk.call('after', 'info'):
            logger.warning("中止，正在执行其他的批量任务")
            return
        try:
            character_list = list(self.temporary_strategy["lineups"][self.lineup_focus])
            character_list.reverse()
            i = 0
            for character_name in character_list:
                self.character_check_button[character_name].invoke()
                # i += 1
                # self.after(20 * i, lambda name=character_name: self.character_check_button[
                #     name].invoke())
        except:
            logger.critical("错误，批量任务执行失败，任务:reject_all")

    def switch_win_topmost(self):
        self.is_win_topmost = not self.is_win_topmost
        if self.is_win_topmost:
            self.attributes('-topmost', True)
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
        self.reject_all()
        self.load_temporary_strategy(name)
        self.destroy_temporary_strategy_items()
        self.build_strategy_items()

    def import_strategy(self):
        pass

    def generate_strategy(self):
        if not self.win_new_strategy_name_entry:
            width = self.gui_config.default.win_new_strategy_name.width
            height = self.gui_config.default.win_new_strategy_name.height
            title_height = self.gui_config.default.win_new_strategy_name.title.height
            bg = self.gui_config.default.win_new_strategy_name.bg
            fg = self.gui_config.default.win_new_strategy_name.fg
            scn_w, scn_h = win32api.GetSystemMetrics(win32con.SM_CXSCREEN), win32api.GetSystemMetrics(
                win32con.SM_CYSCREEN)
            cen_x = (scn_w - width) / 2
            cen_y = (scn_h - height) / 2
            self.win_new_strategy_name.overrideredirect(True)
            self.win_new_strategy_name.attributes('-topmost', True)
            # self.win_new_strategy_name.resizable(0, 0)
            g_conf = "%dx%d+%d+%d" % (width, height, cen_x, cen_y)
            self.win_new_strategy_name.geometry(g_conf)
            ft = tf.Font(family='仿宋', size=15, weight=tf.BOLD)
            title_frame = tk.Frame(
                self.win_new_strategy_name,
                width=width,
                height=title_height,
                bg=bg
            )
            title_frame.grid_propagate(False)
            title_frame.grid(
                row=0,
                column=0,
                columnspan=2,
                sticky="W"
            )
            tk.Label(
                title_frame,
                text='起个名字吧:',
                font=ft,
                bg=bg,
                fg=fg
            ).grid(
                padx=10,
                pady=10,
            )
            entry_frame = tk.Frame(
                self.win_new_strategy_name,
                width=width,
                height=height / 4
            )
            entry_frame.grid_propagate(False)
            entry_frame.grid(
                row=1,
                column=0,
                columnspan=2
            )
            self.win_new_strategy_name_entry = tk.Entry(
                entry_frame,
                font=ft,
                width=width,
                fg="#f0d264"
            )
            self.win_new_strategy_name_entry.grid(
                ipadx=5,
                ipady=5,
            )
            tk.Button(
                self.win_new_strategy_name,
                text='确认',
                font=ft,
                # bg="#152030",
                fg=bg,
                command=lambda: self.generate_strategy_verify(True)
            ).grid(
                row=2,
                column=0,
                columnspan=1,
                padx=10,
                pady=10,
            )
            tk.Button(
                self.win_new_strategy_name,
                text='取消',
                font=ft,
                command=lambda: self.generate_strategy_verify(False)
            ).grid(
                row=2,
                padx=10,
                pady=10,
                column=1,
                columnspan=1,
            )
        self.show_win(self.win_new_strategy_name)

    def generate_strategy_verify(self, verify):
        if not verify:
            self.win_new_strategy_name_entry.insert(0, "")
        else:
            if new_name := self.win_new_strategy_name_entry.get():
                new_strategy_data = self.get_temporary_strategy_date()
                new_strategy_data["name"] = new_name
                strategy.record(new_strategy_data)
                self.build_win_main_menu()
        self.hide_win(self.win_new_strategy_name)

    def get_lineup_data(self, lineup_name):
        # return self.temporary_strategy["lineups"][lineup_name]._asdict()
        cache_data = []
        lineup_data = self.temporary_strategy["lineups"][lineup_name]
        for character_name in lineup_data:
            cache_data.append(
                {
                    "character": character_name,
                    "equipment": lineup_data[character_name].equipment
                }
            )
        return cache_data

    def get_temporary_strategy_date(self):
        temporary_strategy_data = {
            "early_lineup": self.get_lineup_data("early_lineup"),
            "mid_term_lineup": self.get_lineup_data("mid_term_lineup"),
            "final_lineup": self.get_lineup_data("final_lineup"),
            "thinking": "",
        }
        return temporary_strategy_data

    def export_strategy(self):
        pass

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

    def auth(self):
        user_config = config_parser(config_init.user.path)
        self.win_auth.attributes("-alpha", 0.9)
        self.win_auth.iconbitmap(user_config.gui.common.icon.main.path)
        self.win_auth.configure(background="#203040")
        self.win_auth.title('请输入你的用户KEY')
        self.win_auth.geometry('1020x240')
        self.win_auth.resizable(width=False, height=False)
        self.win_auth.geometry("+300+300")
        # 画布放置图片
        ft = tf.Font(family='仿宋', size=15, weight=tf.BOLD)
        # 标签 用Key
        tk.Label(
            self.win_auth,
            text='用户Key:',
            font=ft,
            bg="#203040",
            fg="#f0d264"
        ).grid(
            column=1,
            row=1,
            ipadx=10,
            ipady=10
        )
        # key输入框
        entry = tk.Entry(self.win_auth,
                         font=ft,
                         width=80,
                         bg="#406080",
                         fg="#f0d264"
                         )
        auth_entry = entry
        entry.grid(
            column=2,
            row=1,
            ipadx=5,
            ipady=5
        )

        def auto_auth():
            auth_file_path = user_config.auth.user_info.path
            auth_user_info = read_all(auth_file_path)
            auth_entry.insert(0, auth_user_info)

        auto_auth()

        def auth():
            auth_url_target = user_config.auth.url
            auth_user_info = auth_entry.get()
            auth_url = auth_url_target + auth_user_info
            res = requests.get(auth_url)
            if res.text == 'OK':
                self.auth_success()
            else:
                msgBox.showwarning('无效KEY', '你输入的KEY为无效KEY')

        tk.Button(
            self.win_auth,
            text='进入程序',
            font=ft,
            bg="#152030",
            fg="#f0d264",
            command=auth
        ).grid(
            column=1,
            row=2,
            ipadx=3,
            ipady=5,
        )
        # 提示信息
        tk.Label(
            self.win_auth,
            text='重要提示！！！：使用1600*900分辨率、无边框模式进行游戏才可放心食用TFTHelper',
            font=ft,
            fg='#DC143C',
            bg="#203040"
        ).grid(
            column=2,
            # columnspan=2,
            row=2,
            ipadx=10,
            ipady=10,
            sticky=tk.W
        )
        tk.Label(
            self.win_auth,
            text='用法：在你按下d键的时候程序自动识别你想要的英雄并向你提示\n特别提示！！！：本程序完全免费！本程序的初衷是为了让大家更好的玩游戏，为了防止不法分子将本软件商用特加上验证用户Key功能，Key加群获取，本程序官方QQ群为893998223，请每一位使用者都加群，一起吹牛，一起下棋，key每隔一段时间就会更新，另外每隔一段时间本程序大版本也会更新，key和新版程序加群获得，如果你是通过付费方式获取的此软件，请向你使用的平台进行举报该商家，最后，祝大家玩得开心!',
            wraplength=980,
            justify='left',
            font=ft,
            fg="#f0d264",
            bg="#203040"
        ).grid(
            column=1,
            columnspan=2,
            row=3,
            ipadx=10,
            ipady=10,
            sticky=tk.W
        )
        self.win_auth.protocol("WM_DELETE_WINDOW", self.quit)
        self.show_win(self.win_auth)
