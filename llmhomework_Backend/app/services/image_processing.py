import cv2
import numpy as np
import os

def preprocess_image(image_path, output_size=None, debug=False):
    """
    改进的图片预处理函数 - 针对手写数学作业优化
    Args:
        image_path: 图片路径
        output_size: 输出尺寸，如果为None则保持原始尺寸
        debug: 是否保存调试图片
    """
    steps = {}
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    
    steps['original'] = img.copy()
    
    # 1. 尺寸标准化 - 确保图片足够大以便OCR识别
    h, w = img.shape[:2]
    if min(h, w) < 800:
        # 放大图片，提高OCR识别率
        scale = 800 / min(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        print(f"图片尺寸从 {w}x{h} 放大到 {new_w}x{new_h}")
    
    # 2. 降噪处理
    img = cv2.bilateralFilter(img, 9, 75, 75)
    
    # 3. 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 4. 对比度增强 - 使手写字迹更清晰
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # 5. 自适应阈值 - 处理光照不均
    binary = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY, 11, 2)
    
    # 6. 形态学操作 - 清理噪点
    kernel = np.ones((2,2), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
    
    
    steps['enhanced'] = enhanced
    steps['binary'] = binary
    steps['cleaned'] = cleaned
    
    # 8. 保存最终处理结果
    name, ext = os.path.splitext(image_path)
    processed_path = f"{name}_processed{ext}"
    
    # 保存清理后的二值化图像，这样OCR效果更好
    cv2.imwrite(processed_path, cleaned)
    
    print(f"图片预处理完成: {processed_path}")
    
    if debug:
        # 保存所有处理步骤的图像用于调试
        for k, v in steps.items():
            save_path = f"{name}_{k}{ext}"
            cv2.imwrite(save_path, v)
            print(f"调试图片已保存: {save_path}")
    
    return processed_path
