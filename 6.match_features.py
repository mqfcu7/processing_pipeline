# -*- coding: cp936 -*-
import cv2
import numpy as np
import os
import random
import time

possible_area_y1 = 0.0
possible_area_y2 = 1.0

def detect_brand_roi(img):    
    rows, columns, channels = img.shape
    y1_offset = int(possible_area_y1 * rows)
    y2_offset = int(possible_area_y2 * rows)
    return img[y1_offset : y2_offset]
                                       
    
def match_features(feature, matcher, des1, des2,
                   good_match_distance_ratio = 0.7):
    # find the keypoints and descriptors with SIFT
    matches = matcher.knnMatch(des1, des2, k = 2)
##    print len(des1), len(des2), len(matches)
    num_good_matches = 0
    # ratio test as per Lowe's paper
    for i in xrange(len(matches)):
        try:
            m, n = matches[i]
            if m.distance < good_match_distance_ratio * n.distance:
                num_good_matches = num_good_matches + 1
        except:
            continue
    return num_good_matches

def init_feature(feature_type):
    feature_type = feature_type.lower()
    if feature_type == 'sift':
        feature = cv2.SIFT()
        norm = cv2.NORM_L2
    elif feature_type == 'surf':
##        feature = cv2.SURF(hessianThreshold = 800)
        feature = cv2.SURF()
        norm = cv2.NORM_L2
    elif feature_type == 'orb':
        feature = cv2.ORB(nfeatures = 600) # ~= #brisk
##        feature = cv2.ORB()
        norm = cv2.NORM_HAMMING
    elif feature_type == 'brisk':
        feature = cv2.BRISK()
        norm = cv2.NORM_HAMMING
    else:
        feature = None
        norm = None
    return feature, norm
    
def init_matcher(matcher_type, norm):    
    if matcher_type == 'flann':    
        FLANN_INDEX_KDTREE = 1  
        FLANN_INDEX_LSH = 6  
        search_params = dict(checks = 50)   # or pass empty dictionary
        if norm == cv2.NORM_L2:
            flann_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        else:
            flann_params= dict(algorithm = FLANN_INDEX_LSH,
##                               table_number = 6, # 12
##                               key_size = 12,     # 20
##                               multi_probe_level = 1) #2
                               table_number = 12,
                               key_size = 20, 
                               multi_probe_level = 2)
        matcher = cv2.FlannBasedMatcher(flann_params, search_params)
    else:
        matcher = cv2.BFMatcher(norm)
    return matcher

def filename_to_id(fn):
    return fn[:fn.find('_')] + '.jpg'

def main(feature_type, matcher_type):  
    match_file = 'E:\Projects\无牌车识别\华润20140311\match.txt' 
    matches = {}
    reverse_matches = {}
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
                matches[query_id] = {sample_id : None}
            else:
                matches[query_id][sample_id] = None
            if sample_id not in reverse_matches:
                reverse_matches[sample_id] = {query_id : None}
            else:
                reverse_matches[sample_id][query_id] = None
    print len(matches)
    
    feature, norm = init_feature(feature_type)
    matcher = init_matcher(matcher_type, norm)
    
    sample_dir = 'E:\Projects\无牌车识别\华润20140311\detect_car_roi\入口'
    query_dir = 'E:\Projects\无牌车识别\华润20140311\detect_car_roi\出口'    
    sample_files = os.listdir(sample_dir)
    sample_desriptors = []
    for f in sample_files:
        sample_id = filename_to_id(f)
        if sample_id in sample_ids:
            img = cv2.imread(os.path.join(sample_dir, f))
            sample_kp, sample_des = feature.detectAndCompute(
                detect_brand_roi(img), None)
            for query_id in reverse_matches[sample_id]:
                matches[query_id][sample_id] = sample_des
            sample_desriptors.append([sample_id, sample_des])
    print len(sample_desriptors)
        
    num_sampled_sample_imgs = 30
    sampling_ratio = float(num_sampled_sample_imgs + 5) / len(sample_desriptors)
  
    recall = [0] * num_sampled_sample_imgs

    query_files = os.listdir(query_dir)
    num_query_imgs = 0
    for f in query_files:
        query_id = filename_to_id(f)
        if query_id in matches:
            sampled_sample_desriptors = []
            has_ground_truth = False
            for sample_id in matches[query_id]:
                if matches[query_id][sample_id] is not None:
                    has_ground_truth = True
                    sampled_sample_desriptors.append(
                        [sample_id, matches[query_id][sample_id]])
            if not has_ground_truth:
                continue
            num_query_imgs = num_query_imgs + 1
            img = cv2.imread(os.path.join(query_dir, f))
            query_kp, query_des = feature.detectAndCompute(
                detect_brand_roi(img), None)
            for j in xrange(len(sample_desriptors)):           
                if random.random() < sampling_ratio and \
                   sample_desriptors[j][0] not in matches[query_id]:
                    sampled_sample_desriptors.append(sample_desriptors[j])                
            sampled_sample_desriptors = sampled_sample_desriptors[ \
                : num_sampled_sample_imgs]
            results = []
            for j in xrange(len(sampled_sample_desriptors)):
                num_good_matches = match_features(
                    feature, matcher, query_des, \
                    sampled_sample_desriptors[j][1])
                results.append([num_good_matches, \
                                sampled_sample_desriptors[j][0]])
            results.sort(reverse = True)
            bingo = 0
            for j in xrange(len(results)):
                if results[j][1] in matches[query_id]:
                    recall[j] = recall[j] + 1
                    bingo = 1
                    break
            if not bingo:
                print query_id
    out = open('match_features_recall.csv', 'a')
    out.write(feature_type + ',')
    for j in xrange(1, len(recall)):
        recall[j] = recall[j] + recall[j - 1]
    num_query_imgs = float(num_query_imgs)
    for j in xrange(len(recall)):
##        recall[j] = recall[j] / num_query_imgs
        out.write('%f,' % recall[j])
    out.write('\n')
    out.close()

        
if __name__ == '__main__':
##    http://docs.opencv.org/modules/video/doc/motion_analysis_and_object_tracking.html?highlight=backgroundsubtractormog#backgroundsubtractormog2-backgroundsubtractormog2
    feature_types = ['SIFT', 'SURF', 'ORB', 'BRISK']
    matcher_types = ['brute_force', 'FLANN']
    out = open('match_features_recall.csv', 'w')
    out.close()
    for i in xrange(0, len(feature_types)):
        start = time.time()
        main(feature_types[i], matcher_types[0])
        duration = time.time() - start
        print feature_types[i], duration


##SIFT 550.631000042
##SURF 1212.15699983
##ORB 125.559999943
##BRISK 47.1719999313
