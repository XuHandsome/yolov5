# -*- coding: utf-8 -*-

import sys
import os.path
import subprocess
import time
import mss
from faker import Factory
from system_hotkey import SystemHotkey
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidget, QPushButton, QApplication, QVBoxLayout, QTableWidgetItem, QHeaderView, QLabel, QLineEdit
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont

class ScreenShot(QWidget):

    # 定义一个热键信号
    sig_keyhot = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # 设置自定义热键相应函数
        self.sig_keyhot.connect(self.MKey_pressEvent)

        # 初始化hk_ss热键
        self.hk_ss = SystemHotkey()

        # 绑定快捷键和对应的信号发送函数
        self.hk_ss.register(('alt', 'v'), callback=lambda x: self.send_key_event("screenshot"))

        self.setupUI()
        self.id = 1
        self.lines = []
        self.editable = True
        self.des_sort = True
        self.faker = Factory.create()
        self.btn_select.clicked.connect(self.select)
        self.btn_open.clicked.connect(self.opendir)
        self.setheader()

    # 热键处理函数
    def MKey_pressEvent(self, i_str):
        row = self.table.rowCount()
        self.table.setRowCount(row + 1)
        nowdate_format_a = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        nowdate_format_b = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        print("按下的按键是%s" % (i_str,))
        if i_str == 'screenshot':
            path_list = self.path_text.text().split("/")
            if len(path_list) >= 2 and path_list[1] == '':
                save_dir = f"{self.path_text.text()}"
            else:
                save_dir = f"{self.path_text.text()}/"
            filename = self.screenshot(save_dir, nowdate_format_b)
            print(nowdate_format_a, filename)
            self.table.setItem(row, 0, QTableWidgetItem(nowdate_format_a))
            self.table.setItem(row, 1, QTableWidgetItem(filename))
            self.id += 1

    # 热键信号发送函数(将外部信号，转化成qt信号)
    def send_key_event(self, i_str):
        self.sig_keyhot.emit(i_str)


    def screenshot(self, filepath, num):
        # file_header = "myscreen-"
        file_header = f"{self.btn_prefix.text()}_"
        with mss.mss() as sct:
            filename = sct.shot(output=f"{filepath}{file_header}{num}.png")
            return filename

    # 选择保存文件夹
    def select(self):
        dir = QtWidgets.QFileDialog.getExistingDirectory(None, "选取文件夹", "E:/")
        self.path_text.setText(dir)

    # 打开保存文件夹
    def opendir(self):
        path_list = self.path_text.text().split("/")
        if len(path_list) >= 2 and path_list[1] == '':
            path = path_list[0]
        else:
            path = self.path_text.text().replace("/", "\\")
        FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
        subprocess.run([FILEBROWSER_PATH, path])

    def setheader(self):
        font = QFont('微软雅黑', 12)
        font.setBold(True)
        self.table.horizontalHeader().setFont(font)  # 设置表头字体
        self.table.setColumnWidth(0,150)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setStyleSheet('QHeaderView::section{background:gray}')
        self.table.horizontalHeader().setFixedHeight(40)

    def setupUI(self):
        font = QFont('微软雅黑', 14)
        font.setBold(True)
        self.setWindowTitle('Quick Screen')
        self.resize(640,480)
        self.table = QTableWidget(self)
        self.space = QLabel()
        self.space.setMinimumHeight(30)
        self.btn_set_prefix = QLabel()
        self.btn_set_prefix.setText("设置截图前缀")
        self.btn_prefix = QLineEdit("quick_screen")
        self.btn_prefix.setMaxLength(12)
        self.btn_prefix.setMaximumWidth(100)
        self.btn_select = QPushButton('选择保存目录')
        self.path_text = QLabel()
        self.path_text.setText("E:/")
        self.path_text.setMinimumHeight(20)
        self.btn_open = QPushButton('打开目录')
        self.btn_help = QLabel()
        self.btn_help.setText("使用帮助👇")
        self.btn_help.setFont(font)
        self.btn_help.setStyleSheet("color:red")
        self.btn_help_des = QLabel()
        self.btn_help_des.setText("'Alt + V'快速截图")
        self.spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.btn_set_prefix)
        self.vbox.addWidget(self.btn_prefix)
        self.vbox.addWidget(self.space)
        self.vbox.addWidget(self.btn_select)
        self.vbox.addWidget(self.path_text)
        self.vbox.addWidget(self.space)
        self.vbox.addWidget(self.btn_open)
        self.vbox.addWidget(self.space)
        self.vbox.addWidget(self.space)
        self.vbox.addWidget(self.space)
        self.vbox.addWidget(self.space)
        self.vbox.addWidget(self.btn_help)
        self.vbox.addWidget(self.btn_help_des)
        self.vbox.addSpacerItem(self.spacerItem)
        self.txt = QLabel()
        self.txt.setMinimumHeight(50)
        self.vbox2 = QVBoxLayout()
        self.vbox2.addWidget(self.table)
        self.vbox2.addWidget(self.txt)
        self.hbox = QHBoxLayout()
        self.hbox.addLayout(self.vbox2)
        self.hbox.addLayout(self.vbox)
        self.setLayout(self.hbox)
        self.table.setColumnCount(2)   ##设置列数
        self.headers = ['时间','截图列表']
        self.table.setHorizontalHeaderLabels(self.headers)
        self.show()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = ScreenShot()
    sys.exit(app.exec_())