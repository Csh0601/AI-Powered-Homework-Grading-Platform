import * as ImageManipulator from 'expo-image-manipulator';
import { Image } from 'react-native';

// 压缩图片
export async function compressImage(uri: string, compress: number = 0.7) {
  const result = await ImageManipulator.manipulateAsync(
    uri,
    [],
    { compress, format: ImageManipulator.SaveFormat.JPEG }
  );
  return result.uri;
}

// 图片转 base64
export async function imageToBase64(uri: string) {
  const result = await ImageManipulator.manipulateAsync(
    uri,
    [],
    { base64: true }
  );
  return result.base64;
}

// 检查图片尺寸
export function checkImageSize(uri: string): Promise<{ width: number; height: number }> {
  return new Promise((resolve, reject) => {
    Image.getSize(
      uri,
      (width, height) => resolve({ width, height }),
      (error) => reject(error)
    );
  });
}
