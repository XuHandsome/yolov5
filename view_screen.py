import torch
import cv2
import numpy as np
from mss import mss

import pyautogui
import math
from pynput.mouse import Controller


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



model = torch.hub.load('./', 'custom', path='./runs/train/exp/weights/best.pt', source='local')
# 置信度阀值
model.conf = 0.50
# 自动混合精度推理
model.amp = True
# 一个box里多个标签
model.multi_label = True
# 指定labels number ,训练用的yaml里定义的每个label number对应的标签
model.classes = 0


sct = mss()
# 选中副显示器
monitor_number = 1
# 可以看每个显示器分辨率来判断显示器编号
# test_imgs = sct.monitors[monitor_number]
# print(test_imgs)
mon = sct.monitors[monitor_number]
# bounding_box = {
#         "top": mon["top"] + 0,
#         "left": mon["left"] + 0,
#         "width": 1792,
#         "height": 1120,
#         "mon": monitor_number,
#     }
bounding_box = {
        "top": mon["top"] + 0,
        "left": mon["left"] + 0,
        "width": 640,
        "height": 400,
        "mon": monitor_number,
    }


while True:
    sct_img = sct.grab(bounding_box)
    # sct_img = sct.grab()
    scr_img = np.array(sct_img)
    scr_img = model(scr_img)

    ############## 鼠标移动
    xmins = scr_img.pandas().xyxy[0]['xmin']
    ymins = scr_img.pandas().xyxy[0]['ymin']
    xmaxs = scr_img.pandas().xyxy[0]['xmax']
    ymaxs = scr_img.pandas().xyxy[0]['ymax']
    ## 信任度
    confidences = scr_img.pandas().xyxy[0]['confidence']
    name = scr_img.pandas().xyxy[0]['name']
    class_list = scr_img.pandas().xyxy[0]['class']

    newlist = []
    for xmin, ymin, xmax, ymax, classitem, conf in zip(xmins, ymins, xmaxs, ymaxs, class_list, confidences):
        if classitem == 0 and conf > 0.5:
            newlist.append([int(xmin), int(ymin), int(xmax), int(ymax), conf])

    # print(newlist)

    # 中心坐标
    for listItem in newlist:
        cdList = []
        xyList = []
        # print(listItem)
        xindex = int(listItem[2] - (listItem[2] - listItem[0]) / 2)
        yindex = int(listItem[3] - (listItem[3] - listItem[1]) / 2)
        mouseModal = Controller()
        x, y = mouseModal.position
        # print(x,y)
        L1 = Line(x, y, xindex, yindex)
        cdList.append(int(L1.getlen()))
        xyList.append([xindex, yindex, listItem[0], listItem[1], listItem[2], listItem[3]])
        minCD = min(cdList)
        game_width = 1792
        game_height = 1120
        for cdItem, xyItem in zip(cdList, xyList):
            print("Move To X: ", int(xyItem[0] - game_width // 2))
            print("Move To Y: ", int(xyItem[1] - (game_height - (xyItem[3] - xyItem[5])) // 2))
            x = int(xyItem[0] - game_width // 2)
            y = int(xyItem[1] - (game_height - (xyItem[3] - xyItem[5])) // 2)
            pyautogui.moveTo(x=x, y=y, duration=2, tween=pyautogui.linear)
    #######################

    # 显示
    cv2.imshow("Screen Realtime", np.array(scr_img.render())[0])
    if (cv2.waitKey(1) & 0xFF) == ord('q'):
        cv2.destroyAllWindows()
        break