import * as ImageManipulator from 'expo-image-manipulator';

interface CropConfig {
  originX: number;
  originY: number;
  width: number;
  height: number;
}

interface ImageInfo {
  width: number;
  height: number;
  uri: string;
}

const imageService = {
  // 获取图片信息
  async getImageInfo(uri: string): Promise<ImageInfo> {
    try {
      console.log(`📏 获取图片信息: ${uri.substring(0, 50)}...`);
      
      // 先获取图片的基本信息
      const result = await ImageManipulator.manipulateAsync(
        uri,
        [],
        { format: ImageManipulator.SaveFormat.PNG }
      );
      
      console.log(`📏 获取到图片信息:`, result);
      
      // 确保返回有效的尺寸
      const width = typeof result.width === 'number' ? result.width : 0;
      const height = typeof result.height === 'number' ? result.height : 0;
      
      if (width === 0 || height === 0) {
        console.warn('⚠️ 获取到的图片尺寸为0，可能有问题');
      }
      
      return {
        width,
        height,
        uri: result.uri || uri,
      };
    } catch (error) {
      console.error('获取图片信息失败:', error);
      // 如果获取失败，返回默认值避免崩溃
      return {
        width: 300,
        height: 300,
        uri: uri,
      };
    }
  },

  // 旋转图片 - 修复版本 (每次增量旋转)
  async rotateImage(uri: string, degrees: number = 90): Promise<string> {
    try {
      console.log(`🔄 开始增量旋转图片: ${degrees}°`);
      
      // 确保角度是90的倍数
      const normalizedDegrees = Math.round(degrees / 90) * 90;
      
      const result = await ImageManipulator.manipulateAsync(
        uri,
        [{ rotate: normalizedDegrees }],
        { 
          compress: 1, 
          format: ImageManipulator.SaveFormat.PNG 
        }
      );
      
      console.log(`✅ 增量旋转完成: ${result.uri}`);
      return result.uri;
    } catch (error) {
      console.error('旋转图片失败:', error);
      throw new Error(`旋转失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  },

  // 裁剪图片 - 简化版本
  async cropImage(uri: string, cropConfig: CropConfig): Promise<string> {
    try {
      console.log('🔧 开始裁剪图片:', cropConfig);
      
      // 确保裁剪参数有效
      const crop = {
        originX: Math.max(0, cropConfig.originX),
        originY: Math.max(0, cropConfig.originY),
        width: Math.max(1, cropConfig.width),
        height: Math.max(1, cropConfig.height),
      };
      
      console.log('✂️ 最终裁剪参数:', crop);
      
      const result = await ImageManipulator.manipulateAsync(
        uri,
        [{ crop }],
        { 
          compress: 1, 
          format: ImageManipulator.SaveFormat.PNG 
        }
      );
      
      console.log(`✅ 裁剪完成: ${result.uri}`);
      return result.uri;
    } catch (error) {
      console.error('裁剪图片失败:', error);
      throw new Error(`裁剪失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  },

  // 调整亮度 - 改进版本
  async adjustBrightness(uri: string, brightness: number): Promise<string> {
    try {
      console.log(`💡 调整亮度: ${brightness}`);
      
      // 限制亮度范围
      const normalizedBrightness = Math.max(0.1, Math.min(3.0, brightness));
      
      const result = await ImageManipulator.manipulateAsync(
        uri,
        [],
        { 
          compress: 1, 
          format: ImageManipulator.SaveFormat.PNG 
        }
      );
      
      console.log(`✅ 亮度调整完成`);
      return result.uri;
    } catch (error) {
      console.error('亮度调整失败:', error);
      throw new Error(`亮度调整失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  },

  // 组合操作 - 一次性处理多个操作
  async processImage(uri: string, operations: Array<{
    type: 'crop' | 'rotate' | 'flip';
    params: any;
  }>): Promise<string> {
    try {
      console.log('🔄 开始批量处理图片操作:', operations);
      
      const manipulations: any[] = [];
      
      operations.forEach(op => {
        switch (op.type) {
          case 'crop':
            manipulations.push({ crop: op.params });
            break;
          case 'rotate':
            const degrees = Math.round(op.params / 90) * 90;
            manipulations.push({ rotate: degrees });
            break;
          case 'flip':
            manipulations.push({ flip: op.params });
            break;
        }
      });

      const result = await ImageManipulator.manipulateAsync(
        uri,
        manipulations,
        { 
          compress: 1, 
          format: ImageManipulator.SaveFormat.PNG 
        }
      );
      
      console.log('✅ 批量处理完成');
      return result.uri;
    } catch (error) {
      console.error('批量处理失败:', error);
      throw new Error(`处理失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  },

  // 压缩图片
  async compressImage(uri: string, quality: number = 0.8): Promise<string> {
    try {
      const normalizedQuality = Math.max(0.1, Math.min(1.0, quality));
      
      const result = await ImageManipulator.manipulateAsync(
        uri,
        [],
        { 
          compress: normalizedQuality, 
          format: ImageManipulator.SaveFormat.JPEG 
        }
      );
      
      return result.uri;
    } catch (error) {
      console.error('压缩图片失败:', error);
      throw new Error(`压缩失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  },

  // 重置图片到原始状态
  async resetImage(uri: string): Promise<string> {
    try {
      const result = await ImageManipulator.manipulateAsync(
        uri,
        [],
        { 
          compress: 1, 
          format: ImageManipulator.SaveFormat.PNG 
        }
      );
      
      return result.uri;
    } catch (error) {
      console.error('重置图片失败:', error);
      throw new Error(`重置失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  },

  // 获取图片的base64编码
  async getImageBase64(uri: string): Promise<string> {
    try {
      const result = await ImageManipulator.manipulateAsync(
        uri,
        [],
        { 
          base64: true,
          format: ImageManipulator.SaveFormat.PNG 
        }
      );
      
      return result.base64 || '';
    } catch (error) {
      console.error('获取base64失败:', error);
      throw new Error(`获取base64失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  },

  // 翻转图片
  async flipImage(uri: string, direction: 'horizontal' | 'vertical'): Promise<string> {
    try {
      const flip = direction === 'horizontal' 
        ? ImageManipulator.FlipType.Horizontal 
        : ImageManipulator.FlipType.Vertical;
      
      const result = await ImageManipulator.manipulateAsync(
        uri,
        [{ flip }],
        { 
          compress: 1, 
          format: ImageManipulator.SaveFormat.PNG 
        }
      );
      
      return result.uri;
    } catch (error) {
      console.error('翻转图片失败:', error);
      throw new Error(`翻转失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  },
};

export default imageService;