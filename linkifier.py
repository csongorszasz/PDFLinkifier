import time
import cv2
import pytesseract
import fitz
import numpy as np


def linkify(filepath: str):
    """
    Add a custom contents section to the beginning of a given PDF file, and make song titles searchable.

    Steps:
    - open the file
    - for each page
        - convert the page into an image
        - preprocess the image to make the OCR's job easier
        - look for a title at the top section of the image
        - if found
            - add physical text on top of the title, so that it can be searched
            - save a (title, page_number) for later for the contents page
    """

    doc = fitz.open(filepath)
    page_num = 1
    for page in doc:
        # render page to an image and load it in OpenCV
        pixmap = page.get_pixmap()
        img = cv2.imdecode(np.frombuffer(pixmap.tobytes(), dtype=np.uint8), cv2.IMREAD_GRAYSCALE)

        cv2.imshow("Image", img)
        cv2.waitKey(4000)

        page_num += 1
    cv2.destroyAllWindows()


    # time.sleep(3)

