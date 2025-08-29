import React, { useState, useEffect } from 'react';
import {
  View,
  Image,
  StyleSheet,
  Dimensions,
  Text,
  TouchableOpacity,
  SafeAreaView,
  StatusBar,
  Animated,
} from 'react-native';
import imageService from '../services/imageService';
import { 
  primaryColor, 
  textColor, 
  secondaryTextColor, 
  cardBackgroundColor,
  backgroundColor,
  borderColor,
  successColor,
  systemGray5,
  secondaryColor
} from '../styles/colors';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

interface CropArea {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface ImageCropperProps {
  imageUri: string;
  onCropComplete: (croppedUri: string) => void;
  onCancel: () => void;
}

const ImageCropper: React.FC<ImageCropperProps> = ({
  imageUri,
  onCropComplete,
  onCancel,
}) => {
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });
  const [cropArea, setCropArea] = useState<CropArea>({
    x: 50,
    y: 50,
    width: 200,
    height: 200,
  });
  
  // 动画状态
  const [fadeAnim] = useState(new Animated.Value(0));
  const [slideAnim] = useState(new Animated.Value(50));
  const [scaleAnim] = useState(new Animated.Value(0.9));

  useEffect(() => {
    // 启动进入动画
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 600,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 600,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 50,
        friction: 7,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  const handleImageLoad = (event: any) => {
    const { width, height } = event.nativeEvent;
    setImageSize({ width, height });
    
    // 设置初始裁剪区域为图片中心
    const initialCropSize = Math.min(width, height) * 0.8;
    setCropArea({
      x: (width - initialCropSize) / 2,
      y: (height - initialCropSize) / 2,
      width: initialCropSize,
      height: initialCropSize,
    });
  };

  const adjustCropArea = (direction: 'up' | 'down' | 'left' | 'right' | 'expand' | 'shrink') => {
    const step = 20;
    setCropArea(prev => {
      let newArea = { ...prev };
      
      switch (direction) {
        case 'up':
          newArea.y = Math.max(0, prev.y - step);
          break;
        case 'down':
          newArea.y = Math.min(imageSize.height - prev.height, prev.y + step);
          break;
        case 'left':
          newArea.x = Math.max(0, prev.x - step);
          break;
        case 'right':
          newArea.x = Math.min(imageSize.width - prev.width, prev.x + step);
          break;
        case 'expand':
          const newWidth = Math.min(imageSize.width - prev.x, prev.width + step);
          const newHeight = Math.min(imageSize.height - prev.y, prev.height + step);
          newArea.width = newWidth;
          newArea.height = newHeight;
          break;
        case 'shrink':
          newArea.width = Math.max(50, prev.width - step);
          newArea.height = Math.max(50, prev.height - step);
          break;
      }
      
      return newArea;
    });
  };

  const handleCrop = async () => {
    try {
      // 计算裁剪区域相对于图片的比例
      const scaleX = imageSize.width / screenWidth;
      const scaleY = imageSize.height / screenHeight;
      
      const cropConfig = {
        originX: cropArea.x * scaleX,
        originY: cropArea.y * scaleY,
        width: cropArea.width * scaleX,
        height: cropArea.height * scaleY,
      };

      const result = await imageService.cropImage(imageUri, cropConfig);
      onCropComplete(result);
    } catch (error) {
      console.error('裁剪失败:', error);
      // 在生产环境中，这里应该使用Toast或其他UI组件显示错误
      // 暂时保留console.error用于调试
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor={backgroundColor} />
      
      {/* 渐变背景装饰 */}
      <View style={styles.gradientBackground} />
      
      <Animated.View 
        style={[
          styles.container,
          {
            opacity: fadeAnim,
            transform: [
              { translateY: slideAnim },
              { scale: scaleAnim }
            ]
          }
        ]}
      >
        {/* 顶部导航栏 */}
        <View style={styles.header}>
          <TouchableOpacity onPress={onCancel} style={styles.cancelButton} activeOpacity={0.8}>
            <View style={styles.buttonIconContainer}>
              <Text style={styles.buttonIcon}>✕</Text>
            </View>
            <Text style={styles.cancelButtonText}>取消</Text>
          </TouchableOpacity>
          
          <View style={styles.headerTitleContainer}>
            <View style={styles.titleIconContainer}>
              <Text style={styles.titleIcon}>✂️</Text>
            </View>
            <Text style={styles.headerTitle}>选择裁剪区域</Text>
            <Text style={styles.headerSubtitle}>调整裁剪框位置和大小</Text>
          </View>
          
          <TouchableOpacity onPress={handleCrop} style={styles.confirmButton} activeOpacity={0.9}>
            <Text style={styles.confirmButtonText}>✓ 确定</Text>
          </TouchableOpacity>
        </View>

        {/* 图片容器 */}
        <View style={styles.imageContainer}>
          <View style={styles.imageWrapper}>
            <Image
              source={{ uri: imageUri }}
              style={styles.image}
              onLoad={handleImageLoad}
              resizeMode="contain"
            />
          </View>
          
          {/* 裁剪框 */}
          <View
            style={[
              styles.cropFrame,
              {
                left: cropArea.x,
                top: cropArea.y,
                width: cropArea.width,
                height: cropArea.height,
              },
            ]}
          >
            {/* 裁剪框四角的指示器 */}
            <View style={[styles.cornerIndicator, styles.topLeft]} />
            <View style={[styles.cornerIndicator, styles.topRight]} />
            <View style={[styles.cornerIndicator, styles.bottomLeft]} />
            <View style={[styles.cornerIndicator, styles.bottomRight]} />
            
            {/* 裁剪框中心指示器 */}
            <View style={styles.centerIndicator} />
          </View>

          {/* 半透明遮罩 */}
          <View style={styles.overlay}>
            <View style={[styles.mask, { top: 0, height: cropArea.y }]} />
            <View style={styles.maskRow}>
              <View style={[styles.mask, { left: 0, width: cropArea.x }]} />
              <View style={styles.cropArea} />
              <View style={[styles.mask, { right: 0, width: screenWidth - cropArea.x - cropArea.width }]} />
            </View>
            <View style={[styles.mask, { bottom: 0, height: screenHeight - cropArea.y - cropArea.height }]} />
          </View>
        </View>

        {/* 控制面板 */}
        <View style={styles.controlsContainer}>
          <View style={styles.controlsHeader}>
            <Text style={styles.controlsIcon}>🎯</Text>
            <Text style={styles.controlsTitle}>调整裁剪区域</Text>
          </View>
          
          <View style={styles.controlGrid}>
            <View style={styles.controlRow}>
              <TouchableOpacity 
                style={[styles.controlButton, styles.directionButton]} 
                onPress={() => adjustCropArea('up')}
                activeOpacity={0.8}
              >
                <Text style={styles.controlButtonText}>↑</Text>
              </TouchableOpacity>
            </View>
            <View style={styles.controlRow}>
              <TouchableOpacity 
                style={[styles.controlButton, styles.directionButton]} 
                onPress={() => adjustCropArea('left')}
                activeOpacity={0.8}
              >
                <Text style={styles.controlButtonText}>←</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                style={[styles.controlButton, styles.sizeButton]} 
                onPress={() => adjustCropArea('expand')}
                activeOpacity={0.8}
              >
                <Text style={styles.controlButtonText}>🔍+</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                style={[styles.controlButton, styles.directionButton]} 
                onPress={() => adjustCropArea('right')}
                activeOpacity={0.8}
              >
                <Text style={styles.controlButtonText}>→</Text>
              </TouchableOpacity>
            </View>
            <View style={styles.controlRow}>
              <TouchableOpacity 
                style={[styles.controlButton, styles.directionButton]} 
                onPress={() => adjustCropArea('down')}
                activeOpacity={0.8}
              >
                <Text style={styles.controlButtonText}>↓</Text>
              </TouchableOpacity>
            </View>
            <View style={styles.controlRow}>
              <TouchableOpacity 
                style={[styles.controlButton, styles.sizeButton]} 
                onPress={() => adjustCropArea('shrink')}
                activeOpacity={0.8}
              >
                <Text style={styles.controlButtonText}>🔍-</Text>
              </TouchableOpacity>
            </View>
          </View>

          <View style={styles.instructions}>
            <Text style={styles.instructionText}>
              💡 使用方向按钮调整裁剪区域位置，使用放大/缩小按钮调整大小
            </Text>
          </View>
        </View>
      </Animated.View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: backgroundColor,
  },
  gradientBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 200,
    backgroundColor: 'rgba(88, 86, 214, 0.05)',
    borderBottomLeftRadius: 80,
    borderBottomRightRadius: 80,
  },
  container: {
    flex: 1,
    backgroundColor: 'transparent',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 24,
    backgroundColor: 'transparent',
  },
  cancelButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 59, 48, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(255, 59, 48, 0.2)',
  },
  buttonIconContainer: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: 'rgba(255, 59, 48, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
  buttonIcon: {
    fontSize: 12,
    color: '#FF3B30',
    fontWeight: 'bold',
  },
  cancelButtonText: {
    color: '#FF3B30',
    fontSize: 16,
    fontWeight: '600',
  },
  headerTitleContainer: {
    flex: 1,
    alignItems: 'center',
    marginHorizontal: 20,
  },
  titleIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(88, 86, 214, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  titleIcon: {
    fontSize: 20,
  },
  headerTitle: {
    color: textColor,
    fontSize: 22,
    fontWeight: '800',
    marginBottom: 4,
    textAlign: 'center',
    letterSpacing: -0.5,
  },
  headerSubtitle: {
    color: secondaryTextColor,
    fontSize: 14,
    fontWeight: '500',
    textAlign: 'center',
  },
  confirmButton: {
    backgroundColor: successColor,
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 20,
    shadowColor: successColor,
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  confirmButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
  imageContainer: {
    flex: 1,
    position: 'relative',
    marginHorizontal: 20,
    marginVertical: 20,
  },
  imageWrapper: {
    flex: 1,
    borderRadius: 20,
    overflow: 'hidden',
    backgroundColor: cardBackgroundColor,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 8,
    },
    shadowOpacity: 0.15,
    shadowRadius: 16,
    elevation: 8,
  },
  image: {
    width: '100%',
    height: '100%',
  },
  cropFrame: {
    position: 'absolute',
    borderWidth: 3,
    borderColor: primaryColor,
    backgroundColor: 'transparent',
    shadowColor: primaryColor,
    shadowOffset: {
      width: 0,
      height: 0,
    },
    shadowOpacity: 0.5,
    shadowRadius: 8,
    elevation: 8,
  },
  cornerIndicator: {
    position: 'absolute',
    width: 16,
    height: 16,
    backgroundColor: primaryColor,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 4,
  },
  centerIndicator: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    width: 8,
    height: 8,
    backgroundColor: '#FFFFFF',
    borderRadius: 4,
    marginTop: -4,
    marginLeft: -4,
    borderWidth: 1,
    borderColor: primaryColor,
  },
  topLeft: {
    top: -8,
    left: -8,
  },
  topRight: {
    top: -8,
    right: -8,
  },
  bottomLeft: {
    bottom: -8,
    left: -8,
  },
  bottomRight: {
    bottom: -8,
    right: -8,
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  mask: {
    position: 'absolute',
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
  },
  maskRow: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    flexDirection: 'row',
  },
  cropArea: {
    flex: 1,
  },
  controlsContainer: {
    backgroundColor: cardBackgroundColor,
    padding: 24,
    marginHorizontal: 20,
    marginBottom: 20,
    borderRadius: 24,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 6,
    },
    shadowOpacity: 0.1,
    shadowRadius: 16,
    elevation: 6,
    borderWidth: 1,
    borderColor: 'rgba(0, 0, 0, 0.03)',
  },
  controlsHeader: {
    alignItems: 'center',
    marginBottom: 24,
  },
  controlsIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  controlsTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: textColor,
  },
  controlGrid: {
    marginBottom: 24,
  },
  controlRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 16,
  },
  controlButton: {
    paddingHorizontal: 24,
    paddingVertical: 16,
    borderRadius: 16,
    marginHorizontal: 8,
    minWidth: 70,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 3,
    },
    shadowOpacity: 0.08,
    shadowRadius: 10,
    elevation: 3,
  },
  directionButton: {
    backgroundColor: 'rgba(0, 122, 255, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(0, 122, 255, 0.2)',
  },
  sizeButton: {
    backgroundColor: 'rgba(88, 86, 214, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(88, 86, 214, 0.2)',
  },
  controlButtonText: {
    fontSize: 18,
    fontWeight: '700',
    color: textColor,
  },
  instructions: {
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: 'rgba(0, 122, 255, 0.05)',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(0, 122, 255, 0.1)',
  },
  instructionText: {
    fontSize: 14,
    color: secondaryTextColor,
    textAlign: 'center',
    lineHeight: 20,
    fontWeight: '500',
  },
});

export default ImageCropper; 