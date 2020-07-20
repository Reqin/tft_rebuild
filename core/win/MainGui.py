# coding:utf8
import os
import time
import PyHook3
import pythoncom
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as mgb
from tkinter import PhotoImage
from core.image.image import cv2PIL
from PIL import ImageTk, Image
from threading import Thread
from core.state.state import get_state, set_state
from core.win.ScrollFrame import ScrollableFrame
from core.game_components import character as character_controller
from core.game_components import strategy
from lib import logger
from lib import config_init, config_parser


def start_main_window():
    main_win = MainGui()
    main_win.mainloop()


class MainGui(tk.Tk):
    def __init__(self):
        super().__init__()
        # 加载配置文件
        self.gui_config = config_parser(config_init.user.path).gui
        # 初始化资源
        self.characters = []
        self.head_image = []
        self.strategys = []
        self.temporary_strategy = []
        # 加载资源
        self.load_resource()
        # 窗口资源初始化
        # self:主窗口
        # 当前阵容窗口
        self.win_temporary_strategy = tk.Toplevel()
        # 装备列表窗口
        self.win_equipment_list = tk.Toplevel()
        # 窗口是否置顶
        self.top = False
        # 用于选择人物的check_button
        self.character_check_button = {}
        self.build()

    def load_resource(self):
        self.load_characters()
        self.load_head_image()
        self.load_strategys()
        self.load_temporary_strategy()

    def load_characters(self):
        self.characters = character_controller.all()

    def load_head_image(self):
        for character in self.characters:
            character_head_image_path = character.img_head_path
            photo = Image.open(character_head_image_path)
            photo = photo.resize((self.gui_config.default.win_main.item.photo.width,
                                  self.gui_config.default.win_main.item.photo.height),
                                 Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(photo)
            self.head_image.append(photo)

    def load_strategys(self):
        pass

    def load_temporary_strategy(self):
        self.temporary_strategy = temporary_strategy.all_characters()

    def build(self):

        def ckthwe(event):
            if event.widget != self.win_equipment_list:
                return
            self.hide_win(self.win_equipment_list)

        self.win_equipment_list.bind("<Leave>", ckthwe)
        # 窗口构建
        # 主窗口
        self.build_win_main()
        # 当前阵容窗口
        self.build_win_temporary_strategy(self.win_temporary_strategy)
        # 装备概览窗口
        self.build_win_equipment_list(self.win_equipment_list)
        # 监听键盘
        self.listenKeyboard()

    def build_win_main(self):
        self.build_win_main_outline()

    def build_win_main_outline(self):
        self.set_state(1)
        self.iconbitmap(self.gui_config.common.icon.main.path)
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
        logger.debug(self.gui_config)
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
        menubar = tk.Menu(self)
        menubar.add_cascade(
            label="显示已选", command=lambda: self.showWin(self.win_temporary_strategy)),
        menubar.add_cascade(
            label="隐藏已选", command=lambda: self.hide_win(self.win_temporary_strategy))
        # 自定义阵容
        strategyMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="自定义阵容", menu=strategyMenu)
        strategyMenu.add_command(label='导入', command=self.import_strategy_from_file)
        strategyMenu.add_command(label='导出', command=self.export_strategy)
        strategyMenu.add_command(label='刷新', command=self.refresh_strategy)
        strategyMenu.add_separator()
        # TODO
        strategyNames = []
        for strategyName in strategyNames:
            strategyMenu.add_command(
                label=strategyName, command=lambda x=strategyName: self.import_strategy_from_name(x))

        menubar.add_cascade(label="激活/冻结拿牌功能（快捷键：“F8 ”）",
                            command=self.change_state_then_title)
        menubar.add_cascade(label="全部取消（快捷键：“F9 ”）", command=self.reject_all)
        menubar.add_cascade(label="我全都要（快捷键：“F10”）", command=self.select_all)
        if self.top:
            isTopCon = "取消窗口置顶（快捷键：“F11”）"
        else:
            isTopCon = "设置窗口置顶（快捷键：“F11”）"
        menubar.add_cascade(label=isTopCon, command=self.top_down)
        self.config(menu=menubar)

    def build_win_main_frame(self, master):
        item_width = self.gui_config.default.win_main.item.width
        item_height = self.gui_config.default.win_main.item.height
        # buttonWidth = self.gui_config.default.win_main.item.button.width
        # buttonHeight = self.gui_config.default.win_main.item.button.height
        # photoWidth = self.gui_config.default.win_main.item.button.width
        # photoHeight = self.gui_config.default.win_main.item.button.height
        # selected_color = self.gui_config.default.win_main.item.bg_color
        fg_color = self.gui_config.default.win_main.item.fg_color
        bg_color = self.gui_config.default.win_main.item.bg_color
        num_one_line = self.gui_config.default.win_main.x // self.gui_config.default.win_main.item.width
        i = -1
        for character, photo in zip(self.characters, self.head_image):
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
                text=character.name.ljust(4, chr(12288)),
                fg=fg_color,
                bg=bg_color,
                variable=state,
                command=self.select
            )
            character_check_button.grid(
                row=1,
                column=1,
            )
            character_check_button.state = state
            self.character_check_button[character.name] = character_check_button
            tk.Label(
                item_frame,
                image=photo,
                borderwidth=0,
                relief='ridge',
            ).grid(
                row=2,
                column=1,
                sticky=(tk.W),

            )
        # self.isMainWinReady = True

    def build_win_temporary_strategy(self, win_temporary_strategy):
        win_temporary_strategy.overrideredirect(True)
        win_temporary_strategy.attributes(
            "-alpha", self.gui_config.default.win_temporary_strategy.alpha)
        # 窗口大小
        x = self.gui_config.default.win_temporary_strategy.x
        y = self.gui_config.default.win_temporary_strategy.y
        gconf = str(x) + "x" + str(y)
        win_temporary_strategy.geometry(gconf)
        # 窗口偏移
        gconf = "+" + str(self.gui_config.default.win_temporary_strategy.migration.x) + \
                "+" + str(self.gui_config.default.win_temporary_strategy.migration.y)
        win_temporary_strategy.geometry(gconf)
        win_temporary_strategy.resizable(width=False, height=False)
        self.win_temporary_strategy.grid_propagate(0)
        self.win_temporary_strategy.grid()

        container_frame = tk.Frame(
            win_temporary_strategy,
            bg=self.gui_config.default.win_main.item.bg_color,
            width=x,
            height=y,
            padx=self.gui_config.default.win_temporary_strategy.padx,
            pady=self.gui_config.default.win_temporary_strategy.pady
        )
        container_frame.grid_propagate(0)
        container_frame.grid()

        win_temporary_strategy_frame = ScrollableFrame(
            container_frame,
            width=x,
            height=y,
            highlightthickness=0,
            bg=self.gui_config.default.win_main.item.bg_color
        )
        win_temporary_strategy_frame.grid()
        self.build_win_temporary_strategy_items(win_temporary_strategy_frame)

    def build_win_temporary_strategy_items(self, frame):
        for character in self.temporary_strategy:
            self.select(character, flag=True)

    # 使用
    # self.win_temporary_strategy_frame
    def add_win_temporary_strategy_item(self, character):
        item_width = self.gui_config.default.win_temporary_strategy.item.width
        item_height = self.gui_config.default.win_temporary_strategy.item.height
        bg_color = self.gui_config.default.win_temporary_strategy.item.bg_color
        fg_color = self.gui_config.default.win_temporary_strategy.item.fg_color
        item_image_width = self.gui_config.default.win_temporary_strategy.item.image.width
        item_image_height = self.gui_config.default.win_temporary_strategy.item.image.height
        # 角色渲染区,当需要删除角色渲染时,删除item_frame,item_frame.destroy()
        item_frame = tk.Frame(
            self.win_temporary_strategy_frame.scrollable_frame,
            width=item_width,
            height=item_height,
            bg=bg_color
        )
        self.temporarystrategyItems[character.name] = item_frame
        item_frame.grid_propagate(0)
        item_frame.grid(pady=2)

        # 渲染坐标

        def next(y=[0]):
            y[0] = y[0] + 1
            return y[0]

        # 角色名
        state = self.charactersState[self.allCharactersName.index(
            character.name)]
        nameLabel = tk.Checkbutton(
            item_frame,
            text=character.name.ljust(4, chr(12288)),
            selected_color=self.gui_config.default.win_main.item.bg_color,
            bg=bg_color,
            fg=fg_color,
            variable=state,
            command=lambda name=character.name, state=state: self.select(
                self.temporarystrategyCharacter.resource[name], state)
        )
        nameLabel.grid(
            row=0,
            column=next()
        )
        # 角色相片
        photoLabel = tk.Label(
            item_frame,
            image=self.allCharactersphoto[character.name],
            bg=bg_color,
            fg=fg_color
        )
        photoLabel.grid(
            row=0,
            column=next()
        )
        # 角色装备
        equipments = character.equipmentArea.all()
        for i in range(character.equipmentArea.maxArea):
            if i not in equipments.keys():
                equipmentName = self.gui_config.default.win_equipments_list.empty.name
            else:
                equipmentName = equipments[i].name
            equipmentImg = self.allEquipmentsImg[equipmentName]
            equipmentItem = [tk.Button(
                item_frame,
                image=equipmentImg,
                width=item_image_width,
                height=item_image_height,
                bg=bg_color,
            )][0]
            character.name = character.name

            def func(x, name=character.name, item=equipmentItem, location=i):
                self.focus = {
                    "equipmetItem": item,
                    "character.name": name,
                    "location": location
                }
                self.showwin_equipment_list()

            equipmentItem.bind("<ButtonRelease-1>", func)
            equipmentItem.grid(
                row=0,
                column=next()
            )

    def remove_win_temporary_strategy_item(self, character):
        self.temporarystrategyItems[character.name].destroy()
        pass

    def build_win_equipment_list(self, win_equipment_list):
        return
        win_equipment_list.bind("<ButtonRelease-1>",
                                lambda x: self.hide_win(self.win_equipment_list))
        win_equipment_list.overrideredirect(True)
        win_equipment_list.attributes('-topmost', True)
        win_equipment_list.attributes(
            "-alpha", self.gui_config.default.win_equipments_list.alpha)
        # 窗口大小
        x = self.gui_config.default.win_equipments_list.x
        y = self.gui_config.default.win_equipments_list.y
        gconf = str(x) + "x" + str(y)
        win_equipment_list.geometry(gconf)
        win_equipment_list.resizable(width=False, height=False)
        bg = self.gui_config.default.win_equipments_list.bg_color.default
        self.win_equipment_listFrame = tk.Frame(
            win_equipment_list,
            bg=bg,
            width=x,
            height=y
        )
        self.win_equipment_listFrame.grid_propagate(0)
        self.win_equipment_listFrame.grid()
        num_one_line = self.gui_config.default.win_equipments_list.item_frame.num_one_line
        for name in self.allEquipmentsName:
            i = self.allEquipmentsName.index(name)
            x = i // num_one_line
            y = i % num_one_line
            button = [tk.Button(
                self.win_equipment_listFrame,
                image=self.allEquipmentsImg[name],
                bg=bg
            )][0]
            button.grid(
                row=x,
                column=y
            )

            # self.focus = {
            #         "equipmetItem": item,
            #         "character.name": name,
            #         "location": location
            #     }

            def replace_equipment(x, equipmentButton=button, newEquipmentName=name):
                character = self.temporarystrategyCharacter.resource[self.focus["character.name"]]
                newEquipment = self.aLLEquipmentsEquipment.resource[newEquipmentName]
                state = character.replace_equipment(
                    newEquipment, self.focus["location"])
                if state:
                    self.focus["equipmetItem"]["image"] = equipmentButton["image"]

            button.bind("<ButtonRelease-1>", replace_equipment)

        self.hide_win(win_equipment_list)

    def show_win_equipment_list(self):
        self.show_win(self.win_equipment_list, [
            pag.position()[0] - 5, pag.position()[1] - 5])

    def show_win(self, win, migration=()):
        if migration != ():
            gconf = "+" + str(migration[0]) + "+" + str(migration[1])
            win.geometry(gconf)
        win.update()
        win.deiconify()

    @staticmethod
    def hide_win(win):
        win.withdraw()

    def select_all(self):
        def func():
            while True:
                if self.flag_ws is not True:
                    time.sleep(0.01)
                else:
                    self.flag_ws = False
                    for name in self.allCharactersName:
                        time.sleep(0.001)
                        self.select(
                            self.allCharactersCharacter.resource[name], flag=True)
                    break
            self.flag_ws = True

        task = Thread(target=func)
        task.setDaemon(True)
        task.start()

    def reject_all(self):
        def func():
            while True:
                if self.flag_ws is not True:
                    time.sleep(0.01)
                else:
                    self.flag_ws = False
                    names = list(self.temporarystrategyCharacter.resource.keys())
                    if names is not []:
                        # 实现更加流畅的动画效果
                        names.reverse()
                        for name in names:
                            time.sleep(0.001)
                            self.flag_ws = False
                            self.select(
                                self.allCharactersCharacter.resource[name], flag=False)
                    break
            self.flag_ws = True

        task = Thread(target=func)
        task.setDaemon(True)
        task.start()

    def top_down(self):
        self.top = not self.top
        if self.top:
            self.lift()
            self.attributes('-topmost', True)
            self.win_temporary_strategy.lift()
            self.win_temporary_strategy.attributes('-topmost', True)
        else:
            self.attributes('-topmost', False)
            self.win_temporary_strategy.attributes('-topmost', False)
        self.buildMenu()
        # self.lower()

    def set_state(self, state):
        res = set_state(state)
        if not res:
            logger.warning("状态设置失败，未知的原因，待设置的状态:{}".format(state))
        if state == 1:
            logger.debug(self.gui_config.default)
            self.title(self.gui_config.default.win_main.title.text.positive)
        if state == 0:
            self.title(self.gui_config.default.win_main.title.text.negative)
        # self.setTitle(state)

    def change_state_then_title(self):
        state = get_state()
        state = 1 - state
        self.setStateThenTitle(state)

    def refresh_strategy(self):
        self.buildMenu()

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
            self.select_all()
        if str(key) == 'Key.f11':
            self.top_down()

    # 键盘事件结束

    def select(self, character, state=None, flag=None):
        name = character.name
        if flag is None:
            state = state.get()
        else:
            state = flag
        self.charactersState[self.characters.index(name)].set(state)
        if state:
            if name not in self.temporarystrategyCharacter.resource.keys():
                self.temporarystrategyCharacter.getAlly(character)
                self.add_win_temporary_strategy_item(character)
        else:
            if name in self.temporarystrategyCharacter.resource.keys():
                self.temporarystrategyCharacter.loseAlly(character)
                self.remove_win_temporary_strategy_item(character)
            else:
                log(" 尝试从队伍中删除不存在的角色 " + str(name))
        tellEngine(self.temporarystrategyCharacter)
