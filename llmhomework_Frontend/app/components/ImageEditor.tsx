import Slider from '@react-native-community/slider';
import React, { useState } from 'react';
import { 
  Button, 
  Image, 
  StyleSheet, 
  Text, 
  View, 
  TouchableOpacity, 
  SafeAreaView,
  Animated,
  Dimensions,
  ScrollView,
  StatusBar,
  Alert
} from 'react-native';
import apiService from '../services/apiService';
import imageService from '../services/imageService';
import ImageCropper from './ImageCropper';
import { 
  primaryColor, 
  successColor, 
  textColor, 
  secondaryTextColor, 
  backgroundColor, 
  cardBackgroundColor,
  borderColor,
  systemGray6,
  secondaryColor,
  warningColor,
  systemGray5
} from '../styles/colors';

const { width: screenWidth } = Dimensions.get('window');

interface ImageEditorProps {
  imageUri: string;
  onEditComplete?: (result: any) => void;
}

const ImageEditor: React.FC<ImageEditorProps> = ({ imageUri, onEditComplete }) => {
  const [rotation, setRotation] = useState(0);
  const [brightness, setBrightness] = useState(1);
  const [currentImageUri, setCurrentImageUri] = useState(imageUri);
  const [showCropper, setShowCropper] = useState(false);
  const [fadeAnim] = useState(new Animated.Value(1));
  const [scaleAnim] = useState(new Animated.Value(1));
  const [slideAnim] = useState(new Animated.Value(0));

  // 启动进入动画
  React.useEffect(() => {
    Animated.timing(slideAnim, {
      toValue: 1,
      duration: 600,
      useNativeDriver: true,
    }).start();
  }, []);

  const handleRotate = async () => {
    try {
      // 添加按压动画效果
      Animated.sequence([
        Animated.timing(scaleAnim, {
          toValue: 0.95,
          duration: 100,
          useNativeDriver: true,
        }),
        Animated.timing(scaleAnim, {
          toValue: 1,
          duration: 100,
          useNativeDriver: true,
        }),
      ]).start();

      // 添加淡入淡出动画
      Animated.sequence([
        Animated.timing(fadeAnim, {
          toValue: 0.3,
          duration: 150,
          useNativeDriver: true,
        }),
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
      ]).start();

      const newRotation = rotation + 90;
      setRotation(newRotation);
      
      // 实际应用旋转
      const result = await imageService.rotateImage(currentImageUri, newRotation);
      setCurrentImageUri(result);
    } catch (error) {
      console.error('旋转失败:', error);
      // 在生产环境中，这里应该使用Toast或其他UI组件显示错误
      // 暂时保留console.error用于调试
    }
  };

  const handleBrightnessChange = (value: number) => {
    setBrightness(value);
  };

  const handleCrop = () => {
    setShowCropper(true);
  };

  const handleCropComplete = (croppedUri: string) => {
    setCurrentImageUri(croppedUri);
    setShowCropper(false);
  };

  const handleCropCancel = () => {
    setShowCropper(false);
  };

  // 完成编辑，上传图片并回调
  const handleEditComplete = async () => {
    try {
      console.log('开始上传图片...', currentImageUri);
      
      // 智能生成文件名和类型
      let fileName = 'image.jpg';
      let fileType = 'image/jpeg';
      
      if (currentImageUri.startsWith('data:')) {
        // 从data URI中提取MIME类型
        const mimeMatch = currentImageUri.match(/^data:([^;]+);/);
        if (mimeMatch) {
          fileType = mimeMatch[1];
          // 根据MIME类型设置正确的文件扩展名
          if (fileType === 'image/jpeg') {
            fileName = `image_${Date.now()}.jpg`;
          } else if (fileType === 'image/png') {
            fileName = `image_${Date.now()}.png`;
          } else if (fileType === 'image/gif') {
            fileName = `image_${Date.now()}.gif`;
          } else {
            fileName = `image_${Date.now()}.jpg`; // 默认使用jpg
          }
        }
      } else {
        // 对于非data URI，尝试从路径中提取文件名
        const pathParts = currentImageUri.split('/');
        const lastPart = pathParts[pathParts.length - 1];
        if (lastPart && lastPart.includes('.')) {
          fileName = lastPart;
        } else {
          fileName = `image_${Date.now()}.jpg`;
        }
      }
      
      const file = {
        uri: currentImageUri,
        name: fileName,
        type: fileType,
      };
      console.log('上传文件信息:', file);
      
      const result = await apiService.uploadImage(file);
      console.log('后端返回结果:', JSON.stringify(result, null, 2));
      
      if (onEditComplete) {
        console.log('调用onEditComplete回调...');
        onEditComplete(result);
      }
    } catch (e: any) {
      console.error('上传失败:', e);
      Alert.alert('上传失败', `错误: ${e.message || '未知错误'}`);
    }
  };

  if (showCropper) {
    return (
      <ImageCropper
        imageUri={currentImageUri}
        onCropComplete={handleCropComplete}
        onCancel={handleCropCancel}
      />
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor={backgroundColor} />
      
      {/* 渐变背景装饰 */}
      <View style={styles.gradientBackground} />
      
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <Animated.View 
          style={[
            styles.container,
            {
              transform: [{
                translateY: slideAnim.interpolate({
                  inputRange: [0, 1],
                  outputRange: [50, 0],
                })
              }],
              opacity: slideAnim
            }
          ]}
        >
          {/* 顶部导航栏 */}
          <View style={styles.navigationBar}>
            <View style={styles.navIconContainer}>
              <Text style={styles.navIcon}>🎨</Text>
            </View>
            <Text style={styles.navTitle}>图片编辑</Text>
            <Text style={styles.navSubtitle}>调整图片以获得最佳效果</Text>
          </View>

          {/* 图片预览区域 */}
          <View style={styles.imageSection}>
            <View style={styles.imageContainer}>
              <View style={styles.imageWrapper}>
                <Animated.Image
                  source={{ uri: currentImageUri }}
                  style={[
                    styles.image,
                    {
                      transform: [
                        { rotate: `${rotation}deg` },
                        { scale: scaleAnim }
                      ],
                      opacity: brightness,
                    },
                    { opacity: fadeAnim }
                  ]}
                  resizeMode="contain"
                />
                {/* 图片边框装饰 */}
                <View style={styles.imageBorder} />
              </View>
              <View style={styles.imageInfo}>
                <Text style={styles.imageInfoText}>
                  📐 旋转: {rotation}° | 💡 亮度: {Math.round(brightness * 100)}%
                </Text>
              </View>
            </View>
          </View>

          {/* 控制面板 */}
          <View style={styles.controlsSection}>
            {/* 快速操作 */}
            <View style={styles.quickActions}>
              <TouchableOpacity 
                style={[styles.quickActionButton, styles.rotateButton]} 
                onPress={handleRotate}
                activeOpacity={0.8}
              >
                <View style={styles.buttonIconContainer}>
                  <Text style={styles.quickActionIcon}>🔄</Text>
                </View>
                <Text style={styles.quickActionText}>旋转</Text>
                <Text style={styles.buttonHint}>点击旋转90°</Text>
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={[styles.quickActionButton, styles.cropButton]} 
                onPress={handleCrop}
                activeOpacity={0.8}
              >
                <View style={styles.buttonIconContainer}>
                  <Text style={styles.quickActionIcon}>✂️</Text>
                </View>
                <Text style={styles.quickActionText}>裁剪</Text>
                <Text style={styles.buttonHint}>精确裁剪图片</Text>
              </TouchableOpacity>
            </View>

            {/* 亮度调节 */}
            <View style={styles.brightnessSection}>
              <View style={styles.sectionHeader}>
                <View style={styles.titleContainer}>
                  <Text style={styles.sectionIcon}>💡</Text>
                  <Text style={styles.sectionTitle}>亮度调节</Text>
                </View>
                <View style={styles.valueContainer}>
                  <Text style={styles.sectionValue}>{Math.round(brightness * 100)}%</Text>
                </View>
              </View>
              
              <Slider
                style={styles.slider}
                minimumValue={0.2}
                maximumValue={2}
                value={brightness}
                onValueChange={handleBrightnessChange}
                step={0.01}
                minimumTrackTintColor={primaryColor}
                maximumTrackTintColor={systemGray5}
              />
              
              <View style={styles.sliderLabels}>
                <Text style={styles.sliderLabel}>🌙 暗</Text>
                <Text style={styles.sliderLabel}>☀️ 亮</Text>
              </View>
            </View>

            {/* 完成按钮 */}
            <TouchableOpacity 
              style={styles.completeButton} 
              onPress={handleEditComplete}
              activeOpacity={0.9}
            >
              <Text style={styles.completeButtonText}>✨ 完成编辑</Text>
            </TouchableOpacity>
          </View>
        </Animated.View>
      </ScrollView>
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
    height: 300,
    backgroundColor: 'rgba(0, 122, 255, 0.03)',
    borderBottomLeftRadius: 100,
    borderBottomRightRadius: 100,
  },
  scrollView: {
    flex: 1,
  },
  container: {
    flex: 1,
    backgroundColor: 'transparent',
    minHeight: '100%',
  },
  navigationBar: {
    paddingTop: 20,
    paddingBottom: 24,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  navIconContainer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'rgba(0, 122, 255, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  navIcon: {
    fontSize: 28,
  },
  navTitle: {
    fontSize: 32,
    fontWeight: '800',
    color: textColor,
    marginBottom: 8,
    textAlign: 'center',
    letterSpacing: -0.5,
  },
  navSubtitle: {
    fontSize: 16,
    color: secondaryTextColor,
    textAlign: 'center',
    lineHeight: 22,
    fontWeight: '500',
  },
  imageSection: {
    paddingHorizontal: 20,
    marginBottom: 32,
  },
  imageContainer: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 24,
    padding: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 12,
    },
    shadowOpacity: 0.15,
    shadowRadius: 24,
    elevation: 12,
  },
  imageWrapper: {
    position: 'relative',
    borderRadius: 20,
    overflow: 'hidden',
  },
  image: {
    width: '100%',
    height: 380,
    borderRadius: 20,
  },
  imageBorder: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    borderWidth: 2,
    borderColor: 'rgba(0, 122, 255, 0.2)',
    borderRadius: 20,
    pointerEvents: 'none',
  },
  imageInfo: {
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 25,
    alignSelf: 'center',
    marginTop: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  imageInfoText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
  controlsSection: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 32,
    gap: 16,
  },
  quickActionButton: {
    flex: 1,
    backgroundColor: cardBackgroundColor,
    paddingVertical: 24,
    paddingHorizontal: 20,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 6,
    },
    shadowOpacity: 0.1,
    shadowRadius: 16,
    elevation: 6,
    borderWidth: 1,
    borderColor: 'rgba(0, 0, 0, 0.05)',
  },
  rotateButton: {
    borderColor: primaryColor,
    borderWidth: 2,
  },
  cropButton: {
    borderColor: secondaryColor,
    borderWidth: 2,
  },
  buttonIconContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(0, 122, 255, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  quickActionIcon: {
    fontSize: 24,
  },
  quickActionText: {
    color: textColor,
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 4,
  },
  buttonHint: {
    fontSize: 12,
    color: secondaryTextColor,
    textAlign: 'center',
  },
  brightnessSection: {
    backgroundColor: cardBackgroundColor,
    padding: 28,
    borderRadius: 24,
    marginBottom: 32,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 6,
    },
    shadowOpacity: 0.08,
    shadowRadius: 16,
    elevation: 6,
    borderWidth: 1,
    borderColor: 'rgba(0, 0, 0, 0.03)',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sectionIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: textColor,
  },
  valueContainer: {
    backgroundColor: 'rgba(0, 122, 255, 0.1)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(0, 122, 255, 0.2)',
  },
  sectionValue: {
    fontSize: 16,
    fontWeight: '700',
    color: primaryColor,
  },
  slider: {
    width: '100%',
    height: 40,
  },
  sliderThumb: {
    backgroundColor: primaryColor,
    borderWidth: 3,
    borderColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  sliderLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 12,
  },
  sliderLabel: {
    fontSize: 14,
    color: secondaryTextColor,
    fontWeight: '600',
  },
  completeButton: {
    backgroundColor: successColor,
    paddingVertical: 22,
    paddingHorizontal: 36,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: successColor,
    shadowOffset: {
      width: 0,
      height: 10,
    },
    shadowOpacity: 0.4,
    shadowRadius: 20,
    elevation: 10,
  },
  completeButtonGradient: {
    paddingVertical: 22,
    paddingHorizontal: 36,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  completeButtonText: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
});

export default ImageEditor; 