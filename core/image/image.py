import cv2
import numpy as np
from PIL import Image, ImageGrab
from skimage.metrics import structural_similarity


def getImage(path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), -1)


def covGray(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def cv2PIL(img):
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def PIL2cv(img):
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


def standardize(img, x, y):
    try:
        try:
            img = cv2.resize(img, (x, y))
        except:
            img = PIL2cv(img)
            img = cv2.resize(img, (x, y))
    except:
        log(' fail to standardize image ')
    return img


def imgCompare(img1, img2):
    x = defaultConfig["engine.img_standard_size.x"]
    y = defaultConfig["engine.img_standard_size.y"]
    img1 = standardize(img1, x, y)
    img2 = standardize(img2, x, y)
    score = structural_similarity(covGray(img1), covGray(img2), full=True)[0]
    if score > 0.6:
        return True
    else:
        return False


def cutWin(loc):
    img_ready = ImageGrab.grab(loc)
    return cv2.cvtColor(np.asarray(img_ready), cv2.COLOR_RGB2BGR)
