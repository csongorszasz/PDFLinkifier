from typing import Sequence

import cv2
import pytesseract
import fitz
import numpy as np
import unicodedata
import math


def strip_accents(s):
    nfkd_form = unicodedata.normalize('NFKD', s)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def put_bboxes(cv_image):
    img = cv_image.copy()

    img_height = img.shape[0]
    boxes = pytesseract.image_to_boxes(img, lang='hun', config='--psm 7')
    for box in boxes.splitlines():
        if box != "":
            box = box.split(" ")
            c, x_botleft, y_botleft, x_topright, y_topright = box[0], int(box[1]), int(box[2]), int(box[3]), int(box[4])
            cv2.rectangle(img, (x_botleft, img_height-y_botleft), (x_topright, img_height-y_topright), color=(255, 255, 255), thickness=1)
            cv2.putText(img, strip_accents(c), ((x_botleft + x_topright) // 2 - 3, img_height - y_topright + 30), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    #
    # boxes = pytesseract.image_to_data(img, lang='hun', config='--psm 7')
    # for box in boxes.splitlines():
    #     print(box)

    return img


def get_straight_rect_from_cnt(largest_cnt):
    """
    Returns the topleft coordinate, witdth and height of a straight rectangle retrieved from a contour.

    return format: (x,y,w,h)
    """
    return cv2.boundingRect(largest_cnt)


def get_rotated_rect_from_cnt(largest_cnt) -> np.ndarray:
    """
    Returns the corners of a rotated rectangle retrieved from a contour.

    return format: np.ndarray (2d array), where each sublist (row) is an (x,y) pair
    """
    rect = cv2.minAreaRect(largest_cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    return box


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


def preprocess_image(cv_image):
    """Returns a binary image with a single line of text."""

    img = cv_image.copy()

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # grayscale
    img = img[:86, 50:-50]  # crop image to top section

    # blur, threshold
    img = cv2.GaussianBlur(img, (1, 1), 0)
    # cv2.imshow("blurred", img)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    title_bbox = get_title_min_area_rect(img)
    img = crop_to_rotated_rect(img, title_bbox)

    # img = cv2.erode(img, np.ones((1, 1), np.uint8))  # little cleanup
    img = cv2.dilate(img, np.ones((1,1), np.uint8), iterations=1)

    # border
    # border_size = 5
    # img = cv2.copyMakeBorder(img, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=[0,0,0])

    return img


def get_title_line(cv_image):
    return pytesseract.image_to_string(cv_image, lang='hun', config='--psm 7')  # psm 7: treat image as a single line of text


def get_title_words(cv_image):
    return pytesseract.image_to_data(cv_image, lang='hun', config='--psm 7', output_type=pytesseract.Output.DICT)  # psm 7: treat image as a single line of text


def linkify(filepath: str):
    """
    Add a custom contents section to the beginning of a given PDF file, and make song titles searchable.

    Steps:
    - open the file
    - for each page
        - convert the page into an image
        - preprocess the image to make the OCR's job easier
            - mask
            - blur
            - threshold
            - crop image to song title
        - if title is valid
            - add physical text on top of the title, so that it can be searched
            - save a (title, page_number) for later for the contents page
    """

    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    doc = fitz.open(filepath)  # open the pdf
    page_num = 1
    for page in doc:
        pixmap = page.get_pixmap()  # render page to an image
        img = cv2.imdecode(np.frombuffer(pixmap.tobytes(), dtype=np.uint8), cv2.IMREAD_COLOR)  # load it in OpenCV
        img = preprocess_image(img)  # prepare image for OCR

        # title = get_title(img)
        title_data = get_title_words(img)
        print(title_data['conf'], title_data['text'])
        title_str = ""
        for i in range(0, len(title_data['conf'])):
            if title_data['conf'][i] > 0:
                word = title_data['text'][i]
                title_str = f"{title_str} {word}"
        if title_str != "":
            title_str = title_str[1:]
        # else:
        #     continue

        print(title_str)

        cv2.imshow("cropped", img)
        cv2.waitKey(0)

        page_num += 1

    cv2.destroyAllWindows()
