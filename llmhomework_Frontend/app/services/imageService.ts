import * as ImageManipulator from 'expo-image-manipulator';

const imageService = {
  // 裁剪图片
  async cropImage(uri: string, crop: { originX: number; originY: number; width: number; height: number }) {
    const result = await ImageManipulator.manipulateAsync(
      uri,
      [{ crop }],
      { compress: 1, format: ImageManipulator.SaveFormat.PNG }
    );
    return result.uri;
  },

  // 旋转图片
  async rotateImage(uri: string, rotation: number) {
    const result = await ImageManipulator.manipulateAsync(
      uri,
      [{ rotate: rotation }],
      { compress: 1, format: ImageManipulator.SaveFormat.PNG }
    );
    return result.uri;
  },

  // 调整亮度（通过调整对比度和饱和度来模拟亮度效果）
  async adjustBrightness(uri: string, brightness: number) {
    // 使用对比度调整来模拟亮度变化
    const contrast = brightness > 1 ? 1 + (brightness - 1) * 0.5 : brightness;
    const result = await ImageManipulator.manipulateAsync(
      uri,
      [{ contrast }],
      { compress: 1, format: ImageManipulator.SaveFormat.PNG }
    );
    return result.uri;
  },

  // 组合多个操作
  async processImage(uri: string, operations: Array<{
    type: 'crop' | 'rotate' | 'brightness';
    params: any;
  }>) {
    const manipulations: any[] = [];
    
    operations.forEach(op => {
      switch (op.type) {
        case 'crop':
          manipulations.push({ crop: op.params });
          break;
        case 'rotate':
          manipulations.push({ rotate: op.params });
          break;
        case 'brightness':
          // 亮度调整通过对比度实现
          const contrast = op.params > 1 ? 1 + (op.params - 1) * 0.5 : op.params;
          manipulations.push({ contrast });
          break;
      }
    });

    const result = await ImageManipulator.manipulateAsync(
      uri,
      manipulations,
      { compress: 1, format: ImageManipulator.SaveFormat.PNG }
    );
    return result.uri;
  },

  // 压缩图片
  async compressImage(uri: string, quality: number = 0.8) {
    const result = await ImageManipulator.manipulateAsync(
      uri,
      [],
      { compress: quality, format: ImageManipulator.SaveFormat.JPEG }
    );
    return result.uri;
  },

  // 获取图片信息
  async getImageInfo(uri: string) {
    const result = await ImageManipulator.manipulateAsync(
      uri,
      [],
      { base64: true }
    );
    return {
      width: result.width,
      height: result.height,
      base64: result.base64,
    };
  },
};

export default imageService;
