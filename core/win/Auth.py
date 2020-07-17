# coding:utf8
import tkinter as tk
import tkinter.messagebox as msgBox
import tkinter.font as tf
import requests
from lib import logger
from lib import config_init, config_parser
from core.filePipe.pipe import read_all

__AUTH__ = False


def start_auth():
    user_config = config_parser(config_init.user.path)
    window = AuthWindow(user_config)
    window.auto_auth()
    return __AUTH__


def auth():
    pass


class AuthWindow(tk.Tk):
    def __init__(self, user_config):
        super().__init__()
        self.user_config = user_config
        self.auth_entry = None
        self.build()

    def auto_auth(self):
        auth_file_path = self.user_config.auth.user_info.path
        auth_user_info = read_all(auth_file_path)
        self.auth_entry.insert(0, auth_user_info)
        self.mainloop()
        pass

    def auth(self):
        auth_url_target = self.user_config.auth.url
        auth_user_info = self.auth_entry.get()
        auth_url = auth_url_target + auth_user_info
        res = requests.get(auth_url)
        if res.text == 'OK':
            global __AUTH__
            __AUTH__ = True
            self.quit()
            # self.destroy()
        else:
            msgBox.showwarning('无效KEY', '你输入的KEY为无效KEY')

    def build(self):
        self.attributes("-alpha", 0.9)
        self.attributes("-topmost", True)
        self.iconbitmap(self.user_config.gui.common.icon.main.path)
        self.configure(background="#203040")
        self.title('请输入你的用户KEY')
        self.geometry('1020x220')
        self.resizable(width=False, height=False)
        self.geometry("+300+300")
        # 画布放置图片
        ft = tf.Font(family='仿宋', size=15, weight=tf.BOLD)
        # 标签 用Key
        tk.Label(
            self,
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
        entry = tk.Entry(self,
                         font=ft,
                         width=80,
                         bg="#406080",
                         fg="#f0d264"
                         )
        self.auth_entry = entry
        entry.grid(
            column=2,
            row=1,
            ipadx=5,
            ipady=5
        )

        tk.Button(
            self,
            text='进入程序',
            font=ft,
            bg="#152030",
            fg="#f0d264",
            command=self.auth
        ).grid(
            column=1,
            row=2,
            ipadx=3,
            ipady=5,
        )

        # 提示信息
        tk.Label(
            self,
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
            self,
            text='特别提示！！！：本程序完全免费！本程序的初衷是为了让大家更好的玩游戏，为了防止不法分子将本软件商用特加上验证用户Key功能，Key加群获取，本程序官方QQ群为893998223，请每一位使用者都加群，一起吹牛，一起下棋，key每隔一段时间就会更新，另外每隔一段时间本程序大版本也会更新，key和新版本程序加群获得，如果你是通过付费方式获取的此软件，请向你使用的平台进行举报该商家，最后，祝大家把把吃鸡!',
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
