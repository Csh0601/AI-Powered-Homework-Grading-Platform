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

  // 调整亮度（expo-image-manipulator 暂不支持直接亮度调整，这里返回原图，实际可用后端或第三方库实现）
  async adjustBrightness(uri: string, brightness: number) {
    // TODO: 实现亮度调整，可用滤镜库或后端处理
    return uri;
  },
};

export default imageService;
