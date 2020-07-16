# coding:utf8
import os
import time
import copy
import tkinter as tk
import pyautogui as pag
import tkinter.font as tf
import tkinter.filedialog as filedialog
import tkinter.messagebox as mgb
from modules.image.image import cv2PIL
from PIL import ImageTk, Image
from pynput.keyboard import Listener
from threading import Thread
from modules.config.config import defaultConfig as config
from modules.state.state import getState, setState
from modules.filePipe.pipe import pklDump
from modules.log.log import log
from modules.win.ScrollFrame import ScrollableFrame
from modules.creations.Character import Character, loadCharacterHandle, dumpCharacterHandle
from modules.creations.Equipment import Equipment, loadEquipmentsHandle
from modules.creations.lineup import exportLineup, importLineup, getLineupsName


def tellEngine(charactersHandle):
    names = list(charactersHandle.resource.keys())
    path_file = config["engine.path_selected"]
    pklDump(names, path_file)


class MainGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.init()
        self.build()
        self.mainloop()

    # 在这里进行初始化和数据准备
    # 数据准备部分
    # self.allCharactersCharacter           CHaracter实例,character句柄,指向全部可用的character的集合
    # self.aLLEquipmentsEquipment           Equipment实例,Equipment句柄,指向全部可用的Equipment的集合
    # self.temporaryLineupCharacter         CHaracter实例,character句柄,指向当前队伍的character集合
    # self.allCharactersphoto               字典,{name:img},全部人物头像
    # self.allEquipmentsImg                 字典,{name:img},全部装备图片
    # self.temporaryLineupCharactersPhoto   字典,{name:img},当前队伍人物头像
    # self.allCharactersName                列表,存储了所有可用character的名字
    # self.allEquipmentsName                列表,存储了所有可用equipment的名字
    # 窗口更新部分
    # self.charactersState                  列表,用来存储主窗口characterItem.ckB的状态,用字典会产生bug,怀疑是tkinter的设计缺陷
    # self.temporaryLineupItems             字典,由按钮和人物头像,装备图像组成的一个人物表示集合,在窗口self.winTemporaryLineup绘制
    # self.flag_ws                          布尔,用于控制winTemporaryLineup窗口批量操作的动画
    # self.isMainWinReady                   布尔,用于控制初始化时刻主窗口的隐藏/显示,在主窗口渲染完成之前为False,
    #                                       当主窗口渲染完成之后为True
    def init(self):
        # 句柄初始化
        self.temporaryLineupCharacter = Character()
        self.allCharactersCharacter = loadCharacterHandle(
            config["resource.path_characters"])
        self.aLLEquipmentsEquipment = loadEquipmentsHandle(
            config["resource.path_equipments"])
        self.temporaryLineupCharacter = Character()
        # 图像资源初始化
        self.allCharactersphoto = self.loadPhotos(self.allCharactersCharacter)
        self.allEquipmentsImg = self.loadEquipmentsImg(
            self.aLLEquipmentsEquipment)
        # 用于search的名字
        self.allCharactersName = list(self.allCharactersphoto.keys())
        self.allEquipmentsName = list(self.allEquipmentsImg.keys())
        # 窗口关键记录值初始化
        self.charactersState = []
        self.temporaryLineupItems = {}
        self.flag_ws = True
        # TODO
        # 无明显效果,取消
        # self.isMainWinReady = False
        # self.hideWin(self)

    def loadPhotos(self, CharactersHandle):
        photos = {}
        for character in CharactersHandle.resource.values():
            photos[character.name] = ImageTk.PhotoImage(
                (cv2PIL(character.headerImg)))
        return photos

    def loadEquipmentsImg(self, equipmentsHandle):
        imgs = {}
        for equipment in equipmentsHandle.resource.values():
            imgs[equipment.name] = ImageTk.PhotoImage(
                (cv2PIL(equipment.equipmentImg)))
        return imgs

    # 建造各窗口
    # self
    # self.winTemporaryLineup
    # self.winEquipmentsList

    def build(self):
        # 主窗口
        self.buildWinMain()
        # 当前阵容窗口
        self.winTemporaryLineup = tk.Toplevel()
        # 装备概览窗口
        self.winEquipmentsList = tk.Toplevel()

        def ckthwe(event):
            if event.widget != self.winEquipmentsList:
                return
            self.hideWin(self.winEquipmentsList)
        self.winEquipmentsList.bind("<Leave>", ckthwe)
        # 窗口构建
        self.buildWinMain()
        self.buildWinTemporaryLineup(self.winTemporaryLineup)
        self.buildWinEquipmentsList(self.winEquipmentsList)
        # 监听键盘
        self.listenKeyboard()

    def buildWinMain(self):
        self.setStateThenTitle(1)
        self.iconbitmap(config['gui.default.win_main.ico'])
        self.attributes("-alpha", config['gui.default.win_main.alpha'])
        self.x = config['gui.default.win_main.x']
        self.y = config['gui.default.win_main.y']
        geo_conf = str(self.x) + 'x' + str(self.y)
        self.geometry(geo_conf)
        geo_conf = '+' + str(config['gui.default.win_main.migration.x']) + \
            '+' + str(config['gui.default.win_main.migration.y'])
        self.geometry(geo_conf)
        self.resizable(width=config['gui.default.win_main.resizeble.x'],
                       height=config['gui.default.win_main.resizeble.y'])
        # top Down
        self.top = False
        # 动态布局计算
        # 或许不该使用动态计算的布局,而是把布局全做进配置文件中
        itemFrameWidth = config["gui.default.win_main.item.width"]
        numOneLine = self.x // itemFrameWidth
        padx = (self.x % itemFrameWidth) // 2
        bgFrame = tk.Frame(self,
                           bg=config["gui.default.win_main.bgColor.default"],
                           width=self.x,
                           height=self.y)
        mainFrame = tk.Frame(bgFrame,
                             bg=config["gui.default.win_main.bgColor.default"],
                             width=self.x,
                             height=self.y)
        bgFrame.grid_propagate(0)
        bgFrame.grid(
            sticky=(tk.N, tk.E, tk.S, tk.W)
        )
        mainFrame.grid_propagate(0)
        mainFrame.grid(
            padx=padx,
            sticky=(tk.N, tk.E, tk.S, tk.W),
        )
        self.buildMenu()

        # 无效的动作
        # def showWinMain():
        #     while True:
        #         time.sleep(0.01)
        #         if self.isMainWinReady:
        #             self.showWin(self)
        #             self.lift()
        #             self.wm_attributes('-topmost',True)
        #             self.wm_attributes('-topmost',False)
        #             break
        # taskShowWinMain = Thread(target=showWinMain)
        # taskShowWinMain.setDaemon(True)
        # taskShowWinMain.start()
        self.buildMainFrame(mainFrame, numOneLine)

    def buildMenu(self):
        menubar = tk.Menu(self)
        menubar.add_cascade(
            label="显示已选", command=lambda: self.showWin(self.winTemporaryLineup)),
        menubar.add_cascade(
            label="隐藏已选", command=lambda: self.hideWin(self.winTemporaryLineup))
        # 自定义阵容
        lineupMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="自定义阵容", menu=lineupMenu)
        lineupMenu.add_command(label='导入', command=self.importLineupFromFile)
        lineupMenu.add_command(label='导出', command=self.exportLineup)
        lineupMenu.add_command(label='刷新', command=self.refreshLineup)
        lineupMenu.add_separator()
        # TODO
        lineupNames = getLineupsName(config["resource.dir_lineups"])
        for lineupName in lineupNames:
            lineupMenu.add_command(
                label=lineupName, command=lambda x=lineupName: self.importLineupFromName(x))

        menubar.add_cascade(label="激活/冻结拿牌功能（快捷键：“F8 ”）",
                            command=self.changeStateThenTitle)
        menubar.add_cascade(label="全部取消（快捷键：“F9 ”）", command=self.unselectAll)
        menubar.add_cascade(label="我全都要（快捷键：“F10”）", command=self.selectAll)
        if self.top:
            isTopCon = "取消窗口置顶（快捷键：“F11”）"
        else:
            isTopCon = "设置窗口置顶（快捷键：“F11”）"
        menubar.add_cascade(label=isTopCon, command=self.topDown)
        self.config(menu=menubar)

    def buildMainFrame(self, master, numOneLine):
        self.checkButtonsState = []
        itemWidth = config["gui.default.win_main.item.width"]
        itemHeight = config["gui.default.win_main.item.height"]
        # buttonWidth = config["gui.default.win_main.item.button.width"]
        # buttonHeight = config["gui.default.win_main.item.button.height"]
        # photoWidth = config["gui.default.win_main.item.button.width"]
        # photoHeight = config["gui.default.win_main.item.button.height"]
        selectcolor = config["gui.default.win_main.item.bgColor"]
        fgColor = config["gui.default.win_main.item.fgColor"]
        bgColor = config["gui.default.win_main.item.bgColor"]
        for i in range(len(self.allCharactersName)):
            # 避免渲染的画面撕裂
            # time.sleep(0.0001)
            name = self.allCharactersName[i]
            # 坐标计算
            x = i // numOneLine
            y = i % numOneLine
            itemFrame = tk.Frame(
                master,
                width=itemWidth,
                height=itemHeight,
                bg=bgColor
            )
            itemFrame.grid_propagate(0)
            itemFrame.grid(
                row=x,
                column=y,
            )
            characterName = self.allCharactersName[i]
            characterState = tk.BooleanVar()
            self.charactersState.append(characterState)
            characterStateItem = tk.Checkbutton(
                itemFrame,
                text=name.ljust(4, chr(12288)),
                # compound=tk.CENTER,
                selectcolor=selectcolor,
                fg=fgColor,
                bg=bgColor,
                # width=buttonWidth,
                # height=buttonHeight,
                variable=characterState,
                command=lambda name=characterName, state=characterState: self.select(
                    self.allCharactersCharacter.resource[name], state)
            )
            characterStateItem.grid(
                row=1,
                column=1,
            )
            tk.Label(
                itemFrame,
                image=self.allCharactersphoto[name],
                borderwidth=0,
                relief='ridge',
            ).grid(
                row=2,
                column=1,
                sticky=(tk.W),
            )
        self.isMainWinReady = True

    # 广播
    # self.winTemporaryLineupFrame        窗口Frame,当前队伍人物元素渲染的master,用于动态增加元素

    def buildWinTemporaryLineup(self, winTemporaryLineup):
        winTemporaryLineup.overrideredirect(True)
        winTemporaryLineup.attributes(
            "-alpha", config["gui.default.win_temporary_lineup.alpha"])
        # 窗口大小
        x = config["gui.default.win_temporary_lineup.x"]
        y = config["gui.default.win_temporary_lineup.y"]
        gconf = str(x) + "x" + str(y)
        winTemporaryLineup.geometry(gconf)
        # 窗口偏移
        gconf = "+" + str(config["gui.default.win_temporary_lineup.migration.x"]) + \
            "+" + str(config["gui.default.win_temporary_lineup.migration.y"])
        winTemporaryLineup.geometry(gconf)
        winTemporaryLineup.resizable(width=False, height=False)
        self.winTemporaryLineup.grid_propagate(0)
        self.winTemporaryLineup.grid()

        containerFrame = tk.Frame(
            winTemporaryLineup,
            bg=config["gui.default.win_main.item.bgColor"],
            width=x,
            height=y,
            padx=config["gui.default.win_temporary_lineup.padx"],
            pady=config["gui.default.win_temporary_lineup.pady"]
        )
        containerFrame.grid_propagate(0)
        containerFrame.grid()

        self.winTemporaryLineupFrame = ScrollableFrame(
            containerFrame,
            width=x,
            height=y,
            highlightthickness=0,
            # bg=config["gui.default.win_temporary_lineup.bgColor.default"],
            bg=config["gui.default.win_main.item.bgColor"]
        )
        self.winTemporaryLineupFrame.grid()
        self.buildWinTemporaryLineupItems(self.winTemporaryLineupFrame)

    # 广播/使用
    # self.temporaryLineupItems           列表,由按钮和人物头像,装备图像组成的一个人物表示集合,
    #                                     在窗口self.winTemporaryLineup绘制,用于动态删除人物元素
    # 使用
    # self.temporaryLineup                Characters类实例,用于渲染WinTemporaryLineup
    def buildWinTemporaryLineupItems(self, frame):
        for character in self.temporaryLineupCharacter.resource.values():
            self.select(character, flag=True)

    # 使用
    # self.winTemporaryLineupFrame
    def addWinTemporaryLineupItem(self, character):
        itemWidth = config["gui.default.win_temporary_lineup.item.width"]
        itemHeight = config["gui.default.win_temporary_lineup.item.height"]
        bgColor = config["gui.default.win_temporary_lineup.item.bgColor"]
        fgColor = config["gui.default.win_temporary_lineup.item.fgColor"]
        itemImageWidth = config["gui.default.win_temporary_lineup.item.image.width"]
        itemImageHeight = config["gui.default.win_temporary_lineup.item.image.height"]
        # 角色渲染区,当需要删除角色渲染时,删除itemFrame,itemFrame.destroy()
        itemFrame = tk.Frame(
            self.winTemporaryLineupFrame.scrollable_frame,
            width=itemWidth,
            height=itemHeight,
            bg=bgColor
        )
        self.temporaryLineupItems[character.name] = itemFrame
        itemFrame.grid_propagate(0)
        itemFrame.grid(pady=2)
        # 渲染坐标

        def next(y=[0]):
            y[0] = y[0] + 1
            return y[0]
        # 角色名
        state = self.charactersState[self.allCharactersName.index(
            character.name)]
        nameLabel = tk.Checkbutton(
            itemFrame,
            text=character.name.ljust(4, chr(12288)),
            selectcolor=config["gui.default.win_main.item.bgColor"],
            bg=bgColor,
            fg=fgColor,
            variable=state,
            command=lambda name=character.name, state=state: self.select(
                self.temporaryLineupCharacter.resource[name], state)
        )
        nameLabel.grid(
            row=0,
            column=next()
        )
        # 角色相片
        photoLabel = tk.Label(
            itemFrame,
            image=self.allCharactersphoto[character.name],
            bg=bgColor,
            fg=fgColor
        )
        photoLabel.grid(
            row=0,
            column=next()
        )
        # 角色装备
        equipments = character.equipmentArea.all()
        for i in range(character.equipmentArea.maxArea):
            if i not in equipments.keys():
                equipmentName = config["gui.default.win_equipments_list.empty.name"]
            else:
                equipmentName = equipments[i].name
            equipmentImg = self.allEquipmentsImg[equipmentName]
            equipmentItem = [tk.Button(
                itemFrame,
                image=equipmentImg,
                width=itemImageWidth,
                height=itemImageHeight,
                bg=bgColor,
            )][0]
            characterName = character.name

            def func(x, name=characterName, item=equipmentItem, location=i):
                self.focus = {
                    "equipmetItem": item,
                    "characterName": name,
                    "location": location
                }
                self.showWinEquipmentsList()
            equipmentItem.bind("<ButtonRelease-1>", func)
            equipmentItem.grid(
                row=0,
                column=next()
            )

    def removeWinTemporaryLineupItem(self, character):
        self.temporaryLineupItems[character.name].destroy()
        pass

    def buildWinEquipmentsList(self, winEquipmentsList):
        winEquipmentsList.bind("<ButtonRelease-1>",
                               lambda x: self.hideWin(self.winEquipmentsList))
        winEquipmentsList.overrideredirect(True)
        winEquipmentsList.attributes('-topmost', True)
        winEquipmentsList.attributes(
            "-alpha", config["gui.default.win_equipments_list.alpha"])
        # 窗口大小
        x = config["gui.default.win_equipments_list.x"]
        y = config["gui.default.win_equipments_list.y"]
        gconf = str(x) + "x" + str(y)
        winEquipmentsList.geometry(gconf)
        winEquipmentsList.resizable(width=False, height=False)
        bg = config["gui.default.win_equipments_list.bgColor.default"]
        self.winEquipmentsListFrame = tk.Frame(
            winEquipmentsList,
            bg=bg,
            width=x,
            height=y
        )
        self.winEquipmentsListFrame.grid_propagate(0)
        self.winEquipmentsListFrame.grid()
        numOneLine = config["gui.default.win_equipments_list.item_frame.num_one_line"]
        for name in self.allEquipmentsName:
            i = self.allEquipmentsName.index(name)
            x = i // numOneLine
            y = i % numOneLine
            button = [tk.Button(
                self.winEquipmentsListFrame,
                image=self.allEquipmentsImg[name],
                bg=bg
            )][0]
            button.grid(
                row=x,
                column=y
            )
            # self.focus = {
            #         "equipmetItem": item,
            #         "characterName": name,
            #         "location": location
            #     }

            def replaceEquipment(x, equipmentButton=button, newEquipmentName=name):
                character = self.temporaryLineupCharacter.resource[self.focus["characterName"]]
                newEquipment = self.aLLEquipmentsEquipment.resource[newEquipmentName]
                state = character.replaceEquipment(
                    newEquipment, self.focus["location"])
                if state:
                    self.focus["equipmetItem"]["image"] = equipmentButton["image"]
            button.bind("<ButtonRelease-1>", replaceEquipment)

        self.hideWin(winEquipmentsList)

    def showWinEquipmentsList(self):
        self.showWin(self.winEquipmentsList, [
                     pag.position()[0]-5, pag.position()[1]-5])

    def showWin(self, win, migration=()):
        if migration != ():
            gconf = "+" + str(migration[0]) + "+" + str(migration[1])
            win.geometry(gconf)
        win.update()
        win.deiconify()

    def hideWin(self, win):
        win.withdraw()

    def selectAll(self):
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

    def unselectAll(self):
        def func():
            while True:
                if self.flag_ws is not True:
                    time.sleep(0.01)
                else:
                    self.flag_ws = False
                    names = list(self.temporaryLineupCharacter.resource.keys())
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

    def topDown(self):
        self.top = not self.top
        if self.top:
            self.lift()
            self.attributes('-topmost', True)
            self.winTemporaryLineup.lift()
            self.winTemporaryLineup.attributes('-topmost', True)
        else:
            self.attributes('-topmost', False)
            self.winTemporaryLineup.attributes('-topmost', False)
        self.buildMenu()
        # self.lower()

    def setStateThenTitle(self, state):
        setState(state)
        if state == 1:
            self.title(config['gui.default.win_main.title.text.active'])
        if state == 0:
            self.title(config['gui.default.win_main.title.text.inactive'])
        # self.setTitle(state)

    def changeStateThenTitle(self):
        state = getState()
        state = 1 - state
        self.setStateThenTitle(state)

    def refreshLineup(self):
        self.buildMenu()

    def importLineupFromName(self, name):
        file_path = config["resource.dir_lineups"] + name + ".pkl"
        self.importLineupFromFile(file_path)

    def importLineupFromFile(self, file_path=""):
        if file_path == '':
            default_dir = config["resource.root_dir"]
            file_path = filedialog.askopenfilename(
                title=u'从文件导入',
                initialdir=(os.path.expanduser(default_dir)),
                filetypes=[('阵容配置文件', '*.pkl')]
            )
        if file_path == '':
            return
        temporaryLineupCharacter = importLineup(file_path)
        if temporaryLineupCharacter:
            self.unselectAll()
            def selectLineupCharacters():
                while True:
                    if self.flag_ws is not True:
                        time.sleep(0.01)
                    else:
                        time.sleep(0.001)
                        for character in temporaryLineupCharacter.resource.values():
                            self.select(character, flag=True)
                        break
            taskSLC = Thread(target=selectLineupCharacters)
            taskSLC.setDaemon(True)
            taskSLC.start()
        else:
            mgb.showwarning('警告', '不是有效的阵容文件')
            pass

    def exportLineup(self):
        default_dir = config["resource.dir_lineups"]
        file_path = filedialog.asksaveasfilename(
            title=u'导入到文件',
            initialdir=(os.path.expanduser(default_dir)),
            filetypes=[('阵容配置文件', '*.pkl')]
        )
        if file_path == '':
            return
        if file_path[-4:] != '.pkl':
            file_path = file_path + '.pkl'
        if not exportLineup(self.temporaryLineupCharacter, file_path):
            mgb.showwarning("警告","导出阵容文件失败")

    # 键盘事件开始
    def listenKeyboard(self):
        def ifDel():
            with Listener(on_press=self.keyBoardEvent) as listener:
                listener.join()
        t1 = Thread(target=ifDel)
        t1.setDaemon(True)
        t1.start()

    def keyBoardEvent(self, key):

        if str(key) == 'Key.f8':
            self.changeStateThenTitle()
        if str(key) == 'Key.f9':
            self.unselectAll()
        if str(key) == 'Key.f10':
            self.selectAll()
        if str(key) == 'Key.f11':
            self.topDown()
    # 键盘事件结束

    def select(self, character, state=None, flag=None):
        name = character.name
        if flag is None:
            state = state.get()
        else:
            state = flag
        self.charactersState[self.allCharactersName.index(name)].set(state)
        if state:
            if name not in self.temporaryLineupCharacter.resource.keys():
                self.temporaryLineupCharacter.getAlly(character)
                self.addWinTemporaryLineupItem(character)
        else:
            if name in self.temporaryLineupCharacter.resource.keys():
                self.temporaryLineupCharacter.loseAlly(character)
                self.removeWinTemporaryLineupItem(character)
            else:
                log(" 尝试从队伍中删除不存在的角色 " + str(name))
        tellEngine(self.temporaryLineupCharacter)
