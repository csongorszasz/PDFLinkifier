from typing import Sequence

import cv2
import pytesseract
import fitz
import numpy as np
import unicodedata


def strip_accents(s):
    nfkd_form = unicodedata.normalize('NFKD', s)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def get_title_coordinates(cv_image) -> Sequence[int]:
    """Returns the topleft and coordinate, witdth and height (x,y,w,h) of a bounding box that covers the title."""
    img = cv_image.copy()

    # erode, dilate
    img = cv2.erode(img, np.ones((3, 3), np.uint8))  # get rid of any noise
    img = cv2.dilate(img, cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(50, 1)), iterations=1)  # dilate horizontally

    cv2.imshow("dilated", img)

    # find largest contour
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    largest_cnt = max(contours, key=cv2.contourArea)

    return cv2.boundingRect(largest_cnt)


def preprocess_image(cv_image):
    """Returns a binary image with a single line of text."""

    img = cv_image.copy()

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # grayscale
    img = img[:86, 50:-50]  # crop image to top section

    # blur, threshold
    img = cv2.GaussianBlur(img, (1, 1), 0)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # crop image to title
    x, y, w, h = get_title_coordinates(img)
    img = img[(y-5 if y-5 >= 0 else 0):y+h+5, x:x+w]

    img = cv2.erode(img, np.ones((1, 1), np.uint8))  # get rid of any noise


    # border
    border_size = 10
    img = cv2.copyMakeBorder(img, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=[0,0,0])

    return img


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


def get_title(cv_image):
    return pytesseract.image_to_string(cv_image, lang='hun', config='--psm 7')  # psm 7: treat image as a single line of text


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
        - look for a title at the top section of the image
        - if found
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

        print(get_title(img))
        # img = put_bboxes(img)

        cv2.imshow("processed", img)
        cv2.waitKey(0)

        page_num += 1

    cv2.destroyAllWindows()
