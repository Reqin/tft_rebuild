from PIL import ImageFont, ImageDraw, Image
import numpy as np
import os


def load_img(path):
    return Image.open(path)


def p_img(img):
    return Image.fromarray(img.astype('uint8')).convert('RGB')


def n_img(img):
    return np.array(img)


def com_sim(img1, img2):
    vector1 = n_img(img1)
    vector2 = n_img(img2)
    dvd = np.sum(vector2)
    if dvd < 20:
        return 0
    op_r = np.sum(vector1 & vector2) / np.sum(vector2)
    return op_r


def com_sim_text_img(img, text, font_size, ttf_path, canvas_size=()):
    img = get_clean_img(img.convert("L"))
    img_text = draw_text(text, ttf_path, font_size, canvas_size=canvas_size)
    res1 = com_sim(img_text, img)
    img_text = draw_text(text, ttf_path, font_size, y_off=-1, canvas_size=canvas_size)
    res2 = com_sim(img_text, img)
    img_text = draw_text(text, ttf_path, font_size, y_off=1, canvas_size=canvas_size)
    res3 = com_sim(img_text, img)
    return max(res1, res2, res3)


font = False


# 绘图
def draw_text(img_text, ttf_path, font_size, x_off=0, y_off=0, canvas_size=()):
    global font
    if not font:
        font = ImageFont.truetype(ttf_path, font_size)
    canvas = Image.new("RGB", canvas_size, (0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.text((x_off, y_off), img_text, font=font, fill=(255, 255, 255, 255))
    img = canvas.convert("1")
    return img


def get_clean_img(img, threshold=190):
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
