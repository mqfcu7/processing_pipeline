# -*- coding: cp936 -*-
import cv2
import os

sub_dir = '入口'
##sub_dir = '出口'

src_dir = 'E:\Projects\无牌车识别\华润20140311\\' + sub_dir
dst_dir = 'E:\Projects\无牌车识别\华润20140311\equalizeHist\\' + sub_dir
if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)


files = os.listdir(src_dir)
for f in files:
    img = cv2.imread(os.path.join(src_dir, f))
    b,g,r = cv2.split(img)
    b = cv2.equalizeHist(b)
    g = cv2.equalizeHist(g)
    r = cv2.equalizeHist(r)
    img = cv2.merge((b, g, r))
    cv2.imwrite(os.path.join(dst_dir, f), img)
