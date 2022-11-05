# 这里是导入依赖，需要这些库
import math
import sys
import time

import torch
import win32api
import win32con
import win32gui
from PyQt5.QtWidgets import QApplication

import cv2
import numpy as np
from mss import mss

from pynput.mouse import Controller
import mouse


class Point():
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


class Line(Point):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(x1, y1, x2, y2)

    def getlen(self):
        changdu = math.sqrt(math.pow((self.x1 - self.x2), 2) + math.pow((self.y1 - self.y2), 2))
        return changdu

# 截图 mss
def screen_record_mss(l, t, w, h):
    bounding_box = {'top': t, 'left': l, 'width': w, 'height': h}
    with mss() as sct:
        for _ in range(100):
            return sct.grab(bounding_box)

# 截图 pyqt
def screen_record_pyqt(hwnd):
    app = QApplication(sys.argv)
    screen = QApplication.primaryScreen()
    img = screen.grabWindow(hwnd).toImage()
    img.save("ow.bmp")

model = torch.hub.load('./', 'custom', path='./runs/train/exp6/weights/best.pt', source='local')
# 置信度阀值
model.conf = 0.25
# 自动混合精度推理
model.amp = True
# 一个box里多个标签
model.multi_label = True
# 指定labels number ,训练用的yaml里定义的每个label number对应的标签
# model.classes = 0, 1
model.classes = 0

while True:
    # 获取窗口句柄
    # hwnd = win32gui.FindWindow(None, "free_ow_20221030201014.png \u200e- 照片")
    hwnd = win32gui.FindWindow(None, "守望先锋")
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    # 用mss截图推理
    sct_img = screen_record_mss(left, top, width, height)
    scr_img = np.array(sct_img)
    results = model(scr_img)

    # 用pyqt5截图推理
    # screen_record_pyqt(hwnd)
    # img = 'ow.bmp'
    # # 开始推理
    # results = model(img)


    # 显示
    cv2.imshow("Screen Realtime", np.array(results.render())[0])

    # 鼠标移动++++++++++++++++++++++++++++++++++++
    # 过滤模型
    xmins = results.pandas().xyxy[0]['xmin']
    ymins = results.pandas().xyxy[0]['ymin']
    xmaxs = results.pandas().xyxy[0]['xmax']
    ymaxs = results.pandas().xyxy[0]['ymax']
    class_list = results.pandas().xyxy[0]['class']
    confidences = results.pandas().xyxy[0]['confidence']
    newlist = []
    for xmin, ymin, xmax, ymax, classitem, conf in zip(xmins, ymins, xmaxs, ymaxs, class_list, confidences):
        if classitem == 0 and conf > 0.5:
            newlist.append([int(xmin), int(ymin), int(xmax), int(ymax), conf])
    # 循环遍历每个敌人的坐标信息传入距离计算方法获取每个敌人距离鼠标的距离
    if len(newlist) > 0:
        # 存放距离数据
        cdList = []
        xyList = []
        for listItem in newlist:
            # 当前遍历的人物中心坐标
            xindex = int(listItem[2] - (listItem[2] - listItem[0]) / 2)
            yindex = int(listItem[3] - (listItem[3] - listItem[1]) / 2)
            mouseModal = Controller()
            x, y = mouseModal.position
            L1 = Line(x, y, xindex, yindex)
            # 获取到距离并且存放在cdList集合中
            cdList.append(int(L1.getlen()))
            xyList.append([xindex, yindex, listItem[0], listItem[1], listItem[2], listItem[3]])
        minCD = min(cdList)
        print("minCD: ", minCD)
        print("cdList: ", cdList)
        if minCD < 150:
            for cdItem, xyItem in zip(cdList, xyList):
                print("cdItem: ", cdItem)
                if cdItem == minCD:
                    print("x: ", int(xyItem[0] - width // 2), ", y: ", int(xyItem[1] - (height - (xyItem[3] - xyItem[5])) // 2))
                    # 控制鼠标移动到某个点
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(xyItem[0] - width // 2), int(xyItem[1] - (height - (xyItem[3] - xyItem[5])) // 2), 0, 0)
                break
    # ++++++++++++++++++++++++++++++++++++++++++++

    if (cv2.waitKey(1) & 0xFF) == ord('q'):
        cv2.destroyAllWindows()
        break
