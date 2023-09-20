import cv2


def for_large_contours(cv_image):
    img = cv_image.copy()

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (15, 15), 0)
    # cv2.imshow("blur", img)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    # cv2.imshow("thresh", img)
    img = cv2.dilate(img, cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(50, 3)), iterations=1)  # dilate horizontally
    # cv2.imshow("dilate", img)
    cv2.waitKey(0)

    return img


def for_line_of_text(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    return thresh