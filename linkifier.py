import cv2
import pytesseract
import fitz
import numpy as np
import math
import unicodedata

import my


def strip_accents(s):
    nfkd_form = unicodedata.normalize('NFKD', s)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def init_tesseract():
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def add_contents_page_to_doc(doc, titles: list[tuple[int, str]]):
    accented = []
    toc_stripped = []
    idx = 0
    for title in titles:
        title_str = title[1]
        page = title[0]+1
        accented.append(title_str)
        toc_stripped.append([strip_accents(title_str), page, idx])
        idx += 1
    toc_stripped.sort(key=lambda x: x[0])

    toc_final = []
    for i in range(len(titles)):
        title = accented[toc_stripped[i][2]]
        page = toc_stripped[i][1]
        toc_final.append([1, title, page])
    doc.set_toc(toc=toc_final, collapse=0)
    print(f"Table of contents added")


def add_title_to_doc(doc, page_num: int, title: str):
    page = doc[page_num]
    page.insert_text(fitz.Point(30, 30), strip_accents(title), overlay=False)
    print(f"Title added to page {page_num+1}: '{title}'")


def add_titles_to_doc(doc, titles: list[tuple[int, str]]):
    for title in titles:
        add_title_to_doc(doc, title[0], title[1])


def gather_titles(doc) -> list[tuple[int, str]]:
    # doc.select([1,2,33,34,35,36,37,38])

    titles = []  # a list of (page_num, title) pairs
    for page in doc:
        pixmap = page.get_pixmap()  # render page to an image
        img = cv2.imdecode(np.frombuffer(pixmap.tobytes(), dtype=np.uint8), cv2.IMREAD_COLOR)  # load image

        titles_results = my.ocr.get_titles(img)
        for title in titles_results:
            title = title[0].upper() + title[1:]
            titles.append((page.number, title))
            print(f"OCR: {title}")

        # cv2.imshow("img", img)
        # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return titles


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
            - save the titles along with their page number (title, page_number)
    - add physical text on top of the titles, so that they can be searched
    - create table of contents (outline)
    """

    init_tesseract()

    doc = fitz.open(filepath, filetype='.pdf')  # open the pdf
    print(f"> Opened file: {filepath}")

    try:
        titles = gather_titles(doc)
        add_titles_to_doc(doc, titles)
        add_contents_page_to_doc(doc, titles)
    except:
        print("> Error: Something went wrong")
        pass

    doc.save(f"{filepath[:-4]}-feldolgozott.pdf")  # save the modified pdf with a suffix
    doc.close()  # close the pdf
