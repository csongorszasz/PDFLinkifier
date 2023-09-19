import pytesseract
import cv2
import unicodedata

import my


def strip_accents(s):
    nfkd_form = unicodedata.normalize('NFKD', s)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def get_title_as_line(cv_image):
    return pytesseract.image_to_string(cv_image, lang='hun', config='--psm 7')  # psm 7: treat image as a single line of text


def get_title_as_words(cv_image):
    return pytesseract.image_to_data(cv_image, lang='hun', config='--psm 7', output_type=pytesseract.Output.DICT)  # psm 7: treat image as a single line of text


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


def get_titles(img) -> list[str]:
    rois = my.img.extract_rois_from_img(img)
    titles = []
    for roi in rois:
        prepped = my.preprocess.for_line_of_text(roi)
        # cv2.imshow("prepped", prepped)
        if my.img.img_contains_text(prepped):
            title = my.ocr.get_title_as_line(prepped).strip()
            titles.append(title)

            cv2.imshow("selected", prepped)
        # cv2.waitKey(0)

    return titles