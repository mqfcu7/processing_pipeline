# -*- coding: cp936 -*-
import cv2
import os

car_rois = {}
with open('E:\Projects\无牌车识别\华润20140311\car_detection_result_exit.txt') \
     as f:
    for line in f:
        line = line.strip()
        if line:
            line = line.split()
            file_name = line[0]
            if file_name not in car_rois:
                car_rois[file_name] = [[int(x) for x in line[1:]]]
            else:
                car_rois[file_name].append([int(x) for x in line[1:]])
                

src_dir = 'E:\Projects\无牌车识别\华润20140311\出口'
dst_dir = 'E:\Projects\无牌车识别\华润20140311\detect_car_roi\出口'
if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)

files = os.listdir(src_dir)
for f in files:
    if f in car_rois:
        img = cv2.imread(os.path.join(src_dir, f))
        rows, columns, channels = img.shape
        rois = car_rois[f]
        for r in xrange(len(rois)):
            roi = rois[r]
            x = roi[0]
            y = roi[1]
            width = roi[2]
            height = roi[3]
            y_center = y + height / 2
            x_center = x + width / 2
            scale_ratio = 1.3
            y_offset = int(max(0, y_center - height * scale_ratio / 2))
            x_offset = int(max(0, x_center - width * scale_ratio / 2))
            y_end = int(min(rows, y_offset + height * scale_ratio))
            x_end = int(min(columns, x_offset + width * scale_ratio))       
            cv2.imwrite(os.path.join(dst_dir, f[:f.rfind('.')] + '_' + str(r) + '.jpg'),
                        img[y_offset : y_end, x_offset : x_end])
    else:
        print f, ' not found'
