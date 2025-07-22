import easyocr
import pytesseract
import cv2
import numpy as np

# EasyOCR中文识别
EASY_OCR_LANGS = ['ch_sim', 'en']

def ocr_image_easyocr(image_path, gpu=False):
    reader = easyocr.Reader(EASY_OCR_LANGS, gpu=gpu)
    result = reader.readtext(image_path, detail=0)
    return result

# Tesseract中文识别
TES_LANG = 'chi_sim+eng'

def ocr_image_tesseract(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 可加二值化、去噪等预处理
    text = pytesseract.image_to_string(gray, lang=TES_LANG)
    # 按行分割
    return [line.strip() for line in text.split('\n') if line.strip()]

# 统一接口，mode: 'easyocr' or 'tesseract'
def ocr_image(image_path, mode='easyocr', **kwargs):
    if mode == 'easyocr':
        return ocr_image_easyocr(image_path, **kwargs)
    elif mode == 'tesseract':
        return ocr_image_tesseract(image_path)
    else:
        raise ValueError('Unsupported OCR mode')
