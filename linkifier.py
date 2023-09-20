import cv2
import pytesseract
import fitz
import numpy as np
import math

import my


def add_contents_page_to_doc(titles: tuple[int, str]):
    pass


def add_titles_to_doc(titles: tuple[int, str]):
    pass


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
        doc[7],
        # doc[14],
        # doc[17],
        # doc[21],
        # doc[49],
        # doc[71],
        # doc[83],
        # doc[85],
        # doc[100],
        # doc[115],
        # doc[116],
        # doc[119],
        # doc[141],
        # doc[143]
    ]

    titles = []  # a list of (page_num, title) pairs
    for page in doc:
        pixmap = page.get_pixmap()  # render page to an image
        img = cv2.imdecode(np.frombuffer(pixmap.tobytes(), dtype=np.uint8), cv2.IMREAD_COLOR)  # load image

        titles_results = my.ocr.get_titles(img)
        for title in titles_results:
            title = title[0].upper() + title[1:]
            titles.append((page_num, title))

        # cv2.imshow("img", img)
        # cv2.waitKey(0)
        page_num += 1
    # cv2.destroyAllWindows()

    for (page_num, title) in titles:
        print(page_num, title)







