import cv2
import numpy as np
import os

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    # 灰度
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 去噪
    denoised = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
    # 亮度增强
    bright = cv2.convertScaleAbs(denoised, alpha=1.2, beta=30)
    # 旋转校正（简单示例，实际可用HoughLines等）
    processed = bright
    # 修正保存路径
    name, ext = os.path.splitext(image_path)
    processed_path = f"{name}_processed{ext}"
    cv2.imwrite(processed_path, processed)
    return processed_path
