import cv2

import my


def get_rois_from_cnts(img, cnts):
    rois = []
    img_w = img.shape[1]
    for cnt in cnts:
        x, y, w, h = cv2.boundingRect(cnt)
        if 40 < w < img_w-20 and 15 < h < 100:
            # cv2.rectangle(img, (x, y), (x + w, y + h), (36, 255, 12), 2)
            rois.append(img[y:y+h, x:x+w])
    cv2.imshow("contours", img)

    return rois


def get_large_contours(src):
    img = src.copy()

    cnts = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[0])

    return cnts


def resize_img_to_32_multiple(img):
    h, w = img.shape[:2]
    if w % 32 == 0 and h % 32 == 0:
        return img

    img = cv2.resize(img, (320, 320))
    return img


def img_contains_text(img):
    resized = resize_img_to_32_multiple(img)
    cv2.imshow("resized", resized)
    return True


def extract_rois_from_img(img):
    prepped = my.preprocess.for_large_contours(img)
    cnts = get_large_contours(prepped)
    rois = get_rois_from_cnts(img, cnts)
    return rois