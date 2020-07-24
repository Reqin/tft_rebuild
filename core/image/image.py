from PIL import ImageFont, ImageDraw, Image
import numpy as np
import os


# from lib import logger

def load_img(path):
    return Image.open(path)


def p_img(img):
    return Image.fromarray(img.astype('uint8')).convert('RGB')


def n_img(img):
    return np.array(img)


def com_sim(img1, img2):
    vector1 = n_img(img1)
    vector2 = n_img(img2)
    op_r = np.sum(vector1 & vector2) / np.sum(vector2)
    return op_r


def com_sim_text_img(img, text, font_size, ttf_path):
    img = get_clean_img(img.convert("L"))
    img_text = draw_text(text, ttf_path, font_size).convert("1")
    res1 = com_sim(img_text, img)
    img_text = draw_text(text, ttf_path, font_size, y_off=-1).convert("1")
    res2 = com_sim(img_text, img)
    return max(res1, res2)


# 绘图
def draw_text(img_text, ttf_path, font_size, x_off=0, y_off=0, canvas_size=()):
    if canvas_size == ():
        text_len = len(img_text)
        canvas_size = (font_size * text_len, font_size)
    font = ImageFont.truetype(ttf_path, font_size)
    img = Image.new("RGB", canvas_size, (0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((x_off, y_off), img_text, font=font, fill=(255, 255, 255, 255))
    return img


def get_clean_img(img, threshold=200):
    img = n_img(img.convert("L"))
    for x in range(img.shape[0]):
        for y in range(img.shape[1]):
            if img[x][y] > threshold:
                img[x][y] = 255
            else:
                img[x][y] = 0
    return p_img(img).convert("1")


def remove_noise_pixel(b_img):
    img_array = n_img(b_img)
    x_size, y_size = b_img.size
    x_max, y_max = x_size - 2, y_size - 2
    for x in range(y_max):
        i = x + 1
        for y in range(x_max):
            j = y + 1
            check = int(img_array[i - 1][j - 1])
            check = check + img_array[i - 1][j]
            check = check + img_array[i - 1][j + 1]
            check = check + img_array[i][j - 1]
            check = check + img_array[i][j]
            check = check + img_array[i][j + 1]
            check = check + img_array[i + 1][j - 1]
            check = check + img_array[i + 1][j]
            check = check + img_array[i + 1][j + 1]
            if check == 1:
                img_array[i][j] = False
    img_array = np.where(img_array == True, 255, 0)
    return p_img(img_array).convert('1')
