from config import *
from backend.tools import *
from backend.extract import *

import cv2

# ==== вспомогательные инструменты ====
 
# поиск крайних координат указателя
def find_xy_line(image_edited, cx, cy):
    _, contours, _ = cv2.findContours(image_edited,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

    if len(contours) < 1:
        return -1,-1

    max_cntr_index = 0


    def min_Xy(cntr):
        x = 9999
        y = 0
        for p in cntr:
            if x > p[0][0]:
                x = p[0][0]
                y = p[0][1]
        return x,y

    def max_Xy(cntr):
        x = 0
        y = 0
        for p in cntr:
            if x < p[0][0]:
                x = p[0][0]
                y = p[0][1]
        return x,y
    
    def min_Yx(cntr):
        y = 9999
        x = 0
        for p in cntr:
            if y > p[0][1]:
                y = p[0][1]
                x = p[0][0]
        return y, x

    def max_Yx(cntr):
        y = 0
        x = 0
        for p in cntr:
            if y < p[0][1]:
                y = p[0][1]
                x = p[0][0]
        return y, x
    
    # относительно цетра ищем сектор (левый или правый)
    # где находится указатель
    cntr = contours[max_cntr_index]

    minxx = min_Xy(cntr)[0]
    maxyy, maxyx = max_Yx(cntr)[0], max_Yx(cntr)[1]
    minyy =  min_Yx(cntr)[0]

    if minxx < cx:
        if maxyy >= cy and minyy <= cy:
            return maxyx,maxyy
        if maxyy <= cy and minyy < cy:
            return min_Xy(cntr)

    if minxx >= cx:
        if minyy < cy:
            return min_Yx(cntr)[1],minyy
        if minyy == cy:
            return max_Xy(cntr)
        if maxyy > cy:
            return maxyx,maxyy

    return -1,-1

# поиск крайних координат контура надписи "TIM"
def find_xy_tim(max_countors):
    max_x = 99999
    min_x = 0
    x = 0
    for i in max_countors:
        if i[0][0] < max_x:
            max_x = i[0][0]
        if i[0][0] > min_x:
            min_x = i[0][0]
    x = (max_x - min_x)/2+min_x
    return int(x)

# перевести угол в градусы на приборе и добавить смещение от текстовой метки к нулю
def transform_angle(x):
    return int(x/CONST_D1_D2-CONST_BIAS_TIM_TO_ZERO)
