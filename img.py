import cv2
import numpy as np
from imutils.object_detection import non_max_suppression

import my


def extract_rois_from_img(img):
    prepped = my.preprocess.for_large_contours(img)
    # cv2.imshow("prepped", prepped)
    cnts = get_large_contours(prepped)
    rois = get_rois_from_cnts(img, cnts)
    return rois


def get_rois_from_cnts(img, cnts):
    rois = []
    img_w, img_h = img.shape[1], img.shape[0]
    for cnt in cnts:
        x, y, w, h = cv2.boundingRect(cnt)
        if 40 < w < img_w-20 and 13 < h < 100:
            extension_down = y+h+5 if y+h+5<img_h else y+h
            extension_up = y-10 if y-10>=0 else 0
            rois.append(img[extension_up:extension_down, x:x+w])
            # cv2.rectangle(img, (x, y), (x + w, y + h), (36, 255, 12), 2)  # display cnt
            # cv2.imshow("roi", rois[-1])
            # cv2.waitKey(0)
    return rois


def get_large_contours(src):
    img = src.copy()

    cnts = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[0])

    return cnts


def resize_img_with_borders_to_multiple_of_x(img, x: int):
    h, w = img.shape[:2]
    if w % x == 0 and h % x == 0:
        return img

    target_w = (w + x) - ((w + x) % x)  # find the closest larger number than "w" divisible by x
    target_h = (h + x) - ((h + x) % x)  # find the closest larger number than "h" divisible by x

    blank = np.zeros((target_h, target_w), dtype=np.uint8)  # create a blank image of target size
    blank[:h, :w] = img  # put our image on the blank image

    return blank


def resize_img_with_stretching_to_multiple_of_x(img, x: int):
    h, w = img.shape[:2]
    if w % x == 0 and h % x == 0:
        return img, 1, 1

    target_w = (w + x) - ((w + x) % x)  # find the closest larger number than "w" divisible by x
    target_h = (h + x) - ((h + x) % x)  # find the closest larger number than "h" divisible by x

    ratio_w = w / float(target_w)
    ratio_h = h / float(target_h)

    img = cv2.resize(img, (target_w, target_h))
    return img, ratio_w, ratio_h


def img_contains_text(img):
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    resized, ratio_w, ratio_h = resize_img_with_stretching_to_multiple_of_x(img, 32)
    # cv2.imshow("resized", resized)

    layer_names = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]
    net = cv2.dnn.readNet("frozen_east_text_detection.pb")

    h, w = resized.shape[:2]
    blob = cv2.dnn.blobFromImage(resized, 1.0, (w, h), (123.68, 116.78, 103.94), swapRB=True, crop=False)

    net.setInput(blob)
    (scores, geometry) = net.forward(layer_names)

    (num_rows, num_cols) = scores.shape[2:4]

    # FOR BOUNDING BOXES
    # rects = []
    # confidences = []

    min_confidence = 0.98
    for y in range(0, num_rows):
        scores_data = scores[0, 0, y]

        # FOR BOUNDING BOXES
        x_data_0 = geometry[0, 0, y]
        x_data_1 = geometry[0, 1, y]
        x_data_2 = geometry[0, 2, y]
        x_data_3 = geometry[0, 3, y]
        # angles_data = geometry[0, 4, y]

        for x in range(0, num_cols):
            if scores_data[x] < min_confidence:
                continue

            # FOR BOUNDING BOXES
            h_bbox = x_data_0[x] + x_data_2[x]
            w_bbox = x_data_1[x] + x_data_3[x]

            if w_bbox > 40 and h_bbox > 15:
                # print(w_bbox, h_bbox)
                return True

            # FOR BOUNDING BOXES
            # (offset_x, offset_y) = (x * 4.0, y * 4.0)
            #
            # angle = angles_data[x]
            # cos = np.cos(angle)
            # sin = np.sin(angle)
            #
            # end_x = int(offset_x + (cos * x_data_1[x]) + (sin * x_data_2[x]))
            # end_y = int(offset_y - (sin * x_data_1[x]) + (cos * x_data_2[x]))
            # start_x = int(end_x - w_bbox)
            # start_y = int(end_y - h_bbox)
            #
            # rects.append((start_x, start_y, end_x, end_y))
            # confidences.append(scores_data[x])

    # FOR BOUNDING BOXES
    # boxes = non_max_suppression(np.array(rects), probs=confidences)
    #
    # for (start_x, start_y, end_x, end_y) in boxes:
    #     start_x = int(start_x * ratio_w)
    #     start_y = int(start_y * ratio_h)
    #     end_x = int(end_x * ratio_w)
    #     end_y = int(end_y * ratio_h)
    #
    #     img = cv2.rectangle(img, (start_x, start_y), (end_x, end_y), (36, 255, 12), 2)

    return False
