import cv2
import pytesseract
import fitz
import numpy as np
import math
from imutils.object_detection import non_max_suppression

import my


def linkify(filepath: str):
    """
    Add a custom contents section to the beginning of a given PDF file, and make song titles searchable.

    Steps:
    - open the file
    - for each page
        - convert the page into an image
        - preprocess the image
            - grayscale
            - divide the page into large sections
                - blur
                - threshold
                - dilate
        - look for large contours that should mean different sections (title1, music sheet, lyrics, title2, etc.)
        - crop out song titles (if there are any)
        - recognize song titles (if there are any)
            - add physical text on top of the titles, so that they can be searched
            - save the titles along with their page number (title, page_number)
    - create a contents section at the beginning of the document
    """

    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    doc = fitz.open(filepath)  # open the pdf
    page_num = 1

    pages = [
        # doc[0],
        # doc[4],
        doc[26]
    ]
    for page in pages:
        pixmap = page.get_pixmap()  # render page to an image
        img = cv2.imdecode(np.frombuffer(pixmap.tobytes(), dtype=np.uint8), cv2.IMREAD_COLOR)  # load image

        titles = my.ocr.get_titles(img)

        page_num += 1

    cv2.destroyAllWindows()






