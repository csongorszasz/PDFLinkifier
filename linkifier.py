import cv2
import pytesseract
import fitz
import numpy as np


def preprocess_image(cv_image):
    img = cv_image.copy()

    # create a mask for top section of the page, because we are only interested in the title
    mask = np.zeros(img.shape[:2], dtype="uint8")
    cv2.rectangle(mask, (50, 0), (img.shape[1] - 50, 100), 255, -1)

    # blur, threshold, mask
    img = cv2.bitwise_and(img, img, mask=mask)
    img = cv2.GaussianBlur(img, (1, 1), 0)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    return img


def linkify(filepath: str):
    """
    Add a custom contents section to the beginning of a given PDF file, and make song titles searchable.

    Steps:
    - open the file
    - for each page
        - convert the page into an image
        - preprocess the image to make the OCR's job easier
            - mask
        - look for a title at the top section of the image
        - if found
            - add physical text on top of the title, so that it can be searched
            - save a (title, page_number) for later for the contents page
    """

    doc = fitz.open(filepath)  # open the pdf
    page_num = 1
    for page in doc:
        pixmap = page.get_pixmap()  # render page to an image
        img = cv2.imdecode(np.frombuffer(pixmap.tobytes(), dtype=np.uint8), cv2.IMREAD_GRAYSCALE)  # load it in OpenCV
        img = preprocess_image(img)  # prepare image for OCR

        # cv2.imshow("Image", img)
        # cv2.waitKey(0)

        page_num += 1

    # cv2.destroyAllWindows()
