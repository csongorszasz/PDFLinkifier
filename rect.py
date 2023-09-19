import cv2
import numpy as np
import math
from typing import Sequence


# NOT USED
def get_straight_rect_from_cnt(largest_cnt):
    """
    Returns the topleft coordinate, witdth and height of a straight rectangle retrieved from a contour.

    return format: (x,y,w,h)
    """
    return cv2.boundingRect(largest_cnt)


# NOT USED
def get_rotated_rect_from_cnt(largest_cnt) -> np.ndarray:
    """
    Returns the corners of a rotated rectangle retrieved from a contour.

    return format: np.ndarray (2d array), where each sublist (row) is an (x,y) pair
    """
    rect = cv2.minAreaRect(largest_cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    return box


# NOT USED
def get_sub_image_from_rect(src, center, size):
    cx, cy = center
    w, h = int(size[1]), int(size[0])
    if w < h:
        w, h = h, w

    topleft_x = int(cx) - w//2
    topleft_y = int(cy) - h//2

    extended_y_up = topleft_y-5 if topleft_y-5 >= 0 else topleft_y

    # print(f"center: {cx}, {cy}")
    # print(f"size: {w}, {h}")
    # print(f"corner: {topleft_x}, {topleft_y}")
    # print(f"corner_y_ext: {extended_y_up}")

    return src[extended_y_up:topleft_y+h+7, topleft_x:topleft_x+w]


# NOT USED
def crop_to_rotated_rect(src, rect):
    """Returns a cropped image."""
    center, size, angle = rect
    if math.isclose(angle, 90) or math.isclose(angle, 0):
        angle = 0
    elif angle > 45:
        angle = -(90 - angle)
    else:
        angle = -angle

    rot_matr = cv2.getRotationMatrix2D(center, angle, 1)
    dst = cv2.warpAffine(src, rot_matr, src.shape[1:None:-1])
    return get_sub_image_from_rect(dst, center, size)


# NOT USED
def get_title_min_area_rect(cv_image) -> tuple[Sequence[float], Sequence[int], float]:
    """Returns the minimum area rectangle that covers the title."""
    img = cv_image.copy()

    # erode, dilate
    img = cv2.erode(img, np.ones((3, 3), np.uint8))  # get rid of any noise
    img = cv2.dilate(img, np.ones((3, 3), np.uint8))  # add width back to text
    # img = cv2.GaussianBlur(img, (3, 3), 0)
    cv2.imshow("eroded-dilated", img)
    img = cv2.dilate(img, cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(30, 2)), iterations=1)  # dilate horizontally
    cv2.imshow("dilated-horizontally", img)

    # find largest contour
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_cnt_idx = 0
    largest_cnt_area = cv2.contourArea(contours[largest_cnt_idx])
    for i in range(1, len(contours)):
        cnt = contours[i]
        area = cv2.contourArea(cnt)
        height = cv2.boundingRect(cnt)[3]
        if area > largest_cnt_area and height > 10:
            largest_cnt_area = area
            largest_cnt_idx = i

    return cv2.minAreaRect(contours[largest_cnt_idx])