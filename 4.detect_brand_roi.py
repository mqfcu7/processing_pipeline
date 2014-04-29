import cv2
import os
import numpy as np


impossible_area_y1 = 0.4
impossible_area_y2 = 0.85
brand_roi_merge_threashold = 0.025 ## merge areas within 10 pixels
brand_roi_width_low_threashold = 0.05 ## width > 20 pixels is brand area
brand_roi_width_high_threashold = 0.08 ## width < 50 pixels is brand area

def detect_brand_roi(img):
    rows, columns, channels = img.shape
    y1_offset = int(impossible_area_y1 * rows)
    y2_offset = int(impossible_area_y2 * rows)
    return [[y1_offset, y2_offset]]
    possible_rows = y2_offset - y1_offset
    middle_x = columns / 2
    img_left = img[y1_offset : y2_offset, 0 : middle_x]
    img_right = img[y1_offset : y2_offset, middle_x:columns]
    horizontal_projection = np.maximum(img_left.sum(axis = 1),
                                    img_right.sum(axis = 1)).astype(np.float)
    horizontal_projection = np.divide(horizontal_projection,
                                      horizontal_projection.max())
    mean_value = horizontal_projection.mean(axis = 0)
    candidate_areas = []
    is_above_threshold = False
    area = []
    for i in xrange(possible_rows):
        if (horizontal_projection[i] >= mean_value).any():
            if not is_above_threshold:
                is_above_threshold = True
                area.append(i)
        else:
            if is_above_threshold:
                is_above_threshold = False
                area.append(i)
                candidate_areas.append(area)
                area = []
    if is_above_threshold:
        area.append(possible_rows)
        candidate_areas.append(area)
    has_merged_area = True
    while has_merged_area:
        has_merged_area = False
        new_candidate_areas = []
        i = 0
        while i < len(candidate_areas):
            end = candidate_areas[i][1]
            start = candidate_areas[i][0]
            width = end - start
            if width >= brand_roi_width_low_threashold * rows:
                new_candidate_areas.append(candidate_areas[i])
            else:
                if i < len(candidate_areas) - 1:
                    if (candidate_areas[i + 1][0] - end) < \
                       brand_roi_merge_threashold:
                        has_merged_area = True
                        new_candidate_areas.append([start,
                                                  candidate_areas[i + 1][1]])
                        i = i + 1
                else:
                   if (start - candidate_areas[i - 1][1]) < \
                      brand_roi_merge_threashold:
                       has_merged_area = True
                       new_candidate_areas.append([candidate_areas[i - 1][0],
                                                  end])
                       i = i + 1
            i = i + 1

        candidate_areas = new_candidate_areas
    brand_rois = []
    for i in xrange(len(candidate_areas)):
        width = candidate_areas[i][1] - candidate_areas[i][0]
        print width
        if width >= brand_roi_width_low_threashold and width <= \
           brand_roi_width_high_threashold:
            brand_rois.append([y1_offset + y for y in candidate_areas[i]])
    return brand_rois
    
def main():
    src_dir = 'compute_horizontal_gradient'
    dst_dir = 'detect_brand_roi'

    files = os.listdir(src_dir)
    for f in files:
        img = cv2.imread(os.path.join(src_dir, f))
        brand_rois = detect_brand_roi(img)
        img_roi = np.zeros(img.shape)
        for i in range(len(brand_rois)):
            roi = brand_rois[i]
            print roi
            img_roi[roi[0] : roi[1]] = img[roi[0] : roi[1]]
        cv2.imwrite(os.path.join(dst_dir, f), img_roi)
        
if __name__ == '__main__':
    main()
