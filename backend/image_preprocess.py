from PIL import Image, ImageOps, ImageEnhance

def preprocess_image(input_path, output_path):
    img = Image.open(input_path)
    img = ImageOps.exif_transpose(img)  # 自动修正方向
    img = img.convert('L')              # 灰度化
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.1)         # 轻度对比度增强，1.0为原始，1.1为微增强
    img.save(output_path, format='PNG') # 无损保存

# 示例用法
if __name__ == "__main__":
    preprocess_image("test_photo.jpg", "test_photo_pre.png")