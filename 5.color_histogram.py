# -*- coding: cp936 -*-
import cv2
from cv2 import cv
import numpy as np
import os
import time

possible_area_y1 = 0.0
possible_area_y2 = 1.0

def detect_brand_roi(img):    
    rows, columns, channels = img.shape
    y1_offset = int(possible_area_y1 * rows)
    y2_offset = int(possible_area_y2 * rows)
    return img[y1_offset : y2_offset]
                                       
def filename_to_id(fn):
    return fn[:fn.find('_')] + '.jpg'

def calc_histogram(img):
    hbins = 180
    sbins = 255
    hrange = [0,180]
    srange = [0,256]
    ranges = hrange + srange        
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [180, 256], ranges)
    cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
    return hist
    
def main():  
    match_file = 'E:\Projects\无牌车识别\华润20140311\match.txt' 
    matches = {}
    sample_ids = {}
    with open(match_file) as mf:
        for line in mf.readlines():
            line = line.strip().split()
            path = line[0].strip()
            sample_id = path[path.find('\\') + 1:]
            sample_ids[sample_id] = 1
            path = line[1].strip()
            query_id = path[path.find('\\') + 1:]
            if query_id not in matches:
                matches[query_id] = {sample_id : 1}
            else:
                matches[query_id][sample_id] = 1 

    sample_dir = 'E:\Projects\无牌车识别\华润20140311\detect_car_roi\入口'
    query_dir = 'E:\Projects\无牌车识别\华润20140311\detect_car_roi\出口'    
    sample_files = os.listdir(sample_dir)
    sample_imgs = []
    for f in sample_files:
        fid = filename_to_id(f)
        if fid in sample_ids:
            img = cv2.imread(os.path.join(sample_dir, f))
            sample_imgs.append([fid, img])
        else:
            print fid
    print len(sample_imgs)
        
    query_files = os.listdir(query_dir)
    query_imgs = []
    for f in query_files:
        fid = filename_to_id(f)
        if fid in matches:
            img = cv2.imread(os.path.join(query_dir, f))
            query_imgs.append([fid, img])
    print len(query_imgs)
  
    sample_desriptors = []
    for j in xrange(len(sample_imgs)):
        sample_des = calc_histogram(sample_imgs[j][1])
        sample_desriptors.append(sample_des)
        
    query_desriptors = []
    for j in xrange(len(query_imgs)):
        query_des = calc_histogram(query_imgs[j][1])
        query_desriptors.append(query_des)            

    distance_type = [cv.CV_COMP_CORREL, cv.CV_COMP_CHISQR, \
                     cv.CV_COMP_INTERSECT, cv.CV_COMP_BHATTACHARYYA]
    out = open('color_histogram_recall.csv', 'w')
    for t in xrange(len(distance_type)):
        start = time.time() 
        recall = [0] * len(sample_imgs)
        scores = [0] * len(sample_imgs)

        for i in xrange(len(query_imgs)):
            results = []
            query_id = query_imgs[i][0]
            query_des = query_desriptors[i]
            for j in xrange(len(sample_imgs)):
                score = cv2.compareHist(query_des, sample_desriptors[j], \
                                        distance_type[t])
                results.append([score, sample_imgs[j][0]])
            if distance_type[t] == cv.CV_COMP_CORREL or \
               distance_type[t] == cv.CV_COMP_INTERSECT:
                results.sort(reverse = True)
            else:
                results.sort()
            bingo = 0
            for j in xrange(len(sample_imgs)):
                scores[j] = scores[j] + results[j][0]
                if results[j][1] in matches[query_id]:
                    recall[j] = recall[j] + 1
                    bingo = 1
                    break
            if not bingo:
    ##            print query_id
                pass
        for j in xrange(1, len(sample_imgs)):
            recall[j] = recall[j] + recall[j - 1]
        num_unique_query_imgs = float(len(matches))
        for j in xrange(len(sample_imgs)):
    ##        recall[j] = recall[j] / num_query_imgs
            out.write('%f,' % recall[j])
        out.write('\n')
        duration = time.time() - start
        print t, distance_type[t], duration
    out.close()
        
if __name__ == '__main__':
    main()

##0 0 25.1520001888
##1 1 22.6530001163
##2 2 14.2950000763
##3 3 24.1089999676
