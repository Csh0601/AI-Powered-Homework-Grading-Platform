import cv2
import numpy as np
import os

def preprocess_image(image_path, output_size=None, debug=False, for_multimodal=True):
    """
    改进的图片预处理函数 - 支持多模态AI和OCR两种模式
    Args:
        image_path: 图片路径
        output_size: 输出尺寸，如果为None则保持原始尺寸
        debug: 是否保存调试图片
        for_multimodal: 是否为多模态AI处理（保留彩色），否则为OCR处理（二值化）
    """
    steps = {}
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    
    steps['original'] = img.copy()
    
    # 1. 尺寸标准化 - 根据用途调整策略
    h, w = img.shape[:2]
    
    if for_multimodal:
        # 🔥 多模态模式：限制最大尺寸，避免GPU负载过重
        max_dimension = 1600  # 降低最大尺寸
        if max(h, w) > max_dimension:
            scale = max_dimension / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
            print(f"多模态：图片尺寸从 {w}x{h} 缩小到 {new_w}x{new_h}")
        else:
            print(f"多模态：保持原始尺寸 {w}x{h}")
    else:
        # OCR模式：确保图片足够大以便OCR识别
        if min(h, w) < 800:
            scale = 800 / min(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            print(f"OCR：图片尺寸从 {w}x{h} 放大到 {new_w}x{new_h}")
    
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
    
    # 8. 保存最终处理结果 - 根据用途选择不同的输出
    name, ext = os.path.splitext(image_path)
    processed_path = f"{name}_processed{ext}"
    
    if for_multimodal:
        # 多模态AI模式：保存增强的彩色图像，保留更多视觉信息
        # 对彩色图像进行轻微增强但保持原始色彩信息
        enhanced_color = img.copy()
        
        # 轻微锐化增强文字边缘
        kernel_sharp = np.array([[-1,-1,-1],
                                [-1, 9,-1], 
                                [-1,-1,-1]])
        enhanced_color = cv2.filter2D(enhanced_color, -1, kernel_sharp)
        
        # 调整对比度和亮度
        enhanced_color = cv2.convertScaleAbs(enhanced_color, alpha=1.1, beta=10)
        
        cv2.imwrite(processed_path, enhanced_color)
        print(f"图片预处理完成(多模态模式): {processed_path}")
    else:
        # OCR模式：保存二值化图像，提高文字识别率
        cv2.imwrite(processed_path, cleaned)
        print(f"图片预处理完成(OCR模式): {processed_path}")
    
    if debug:
        # 保存所有处理步骤的图像用于调试
        for k, v in steps.items():
            save_path = f"{name}_{k}{ext}"
            cv2.imwrite(save_path, v)
            print(f"调试图片已保存: {save_path}")
    
    return processed_path
