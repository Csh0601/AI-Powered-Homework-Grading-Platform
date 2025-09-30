import React, { useState } from 'react';
import { 
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
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import apiService from '../services/apiService';
import imageService from '../services/imageService';
import ImageCropper from './ImageCropper';
import { DecorativeButton } from './DecorativeButton';
import { RootStackParamList } from '../navigation/NavigationTypes';
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
  taskId?: string;
  onEditComplete?: (result: any) => void; // 保持向后兼容性，但新流程不使用
}

const ImageEditor: React.FC<ImageEditorProps> = ({ imageUri, taskId = 'unknown_task', onEditComplete }) => {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const [rotation, setRotation] = useState(0); // 累积旋转角度
  const [currentImageUri, setCurrentImageUri] = useState(imageUri);
  const [originalImageUri] = useState(imageUri); // 保存原始图片URI
  const [showCropper, setShowCropper] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [scrollViewKey, setScrollViewKey] = useState(0); // 用于强制重新挂载ScrollView
  const [fadeAnim] = useState(new Animated.Value(1));
  const [scaleAnim] = useState(new Animated.Value(1));
  const [slideAnim] = useState(new Animated.Value(0));

  console.log(`\n=== 🎨 [${taskId}] ImageEditor组件加载 ===`);
  console.log(`🎨 [${taskId}] 初始图片URI:`, imageUri.substring(0, 50) + '...');
  console.log(`🎨 [${taskId}] 当前状态 - 旋转: ${rotation}°`);

  // 启动进入动画
  React.useEffect(() => {
    Animated.timing(slideAnim, {
      toValue: 1,
      duration: 600,
      useNativeDriver: true,
    }).start();
  }, []);

  const handleRotate = () => {
    if (isProcessing) return;
    
    console.log(`🔄 [${taskId}] 开始旋转预览...`);
    
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

    // 只更新UI显示角度，不处理实际图片文件
    const newRotation = (rotation + 90) % 360;
    setRotation(newRotation);
    console.log(`🔄 [${taskId}] UI预览角度: ${rotation}° → ${newRotation}°`);
    console.log(`✅ [${taskId}] 预览旋转完成（实际图片将在完成编辑时处理）`);
  };


  const handleCrop = () => {
    setShowCropper(true);
  };

  const handleCropComplete = (croppedUri: string) => {
    console.log(`✂️ [${taskId}] 裁剪完成，返回ImageEditor`);
    setCurrentImageUri(croppedUri);
    setShowCropper(false);
    
    // 强制重新挂载ScrollView，防止手势冲突
    setTimeout(() => {
      setScrollViewKey(prev => prev + 1);
      console.log(`🔄 [${taskId}] 强制重新挂载ScrollView，key: ${scrollViewKey + 1}`);
    }, 100);
  };

  const handleCropCancel = () => {
    console.log(`❌ [${taskId}] 裁剪取消，返回ImageEditor`);
    setShowCropper(false);
    
    // 强制重新挂载ScrollView，防止手势冲突
    setTimeout(() => {
      setScrollViewKey(prev => prev + 1);
      console.log(`🔄 [${taskId}] 强制重新挂载ScrollView，key: ${scrollViewKey + 1}`);
    }, 100);
  };

  // 重置图片到原始状态
  const handleReset = async () => {
    if (isProcessing) return;
    
    try {
      setIsProcessing(true);
      console.log(`🔄 [${taskId}] 重置图片到原始状态...`);
      
      // 重置所有状态到初始值
      setCurrentImageUri(originalImageUri);
      setRotation(0);
      
      console.log(`✅ [${taskId}] 图片重置完成 - 旋转: 0°`);
    } catch (error) {
      console.error(`❌ [${taskId}] 重置失败:`, error);
      Alert.alert('重置失败', `无法重置图片: ${error instanceof Error ? error.message : '未知错误'}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // 完成编辑，准备文件并跳转到加载页面
  const handleEditComplete = async () => {
    try {
      console.log(`\n=== 🚀 [${taskId}] 开始准备批改处理流程 ===`);
      console.log(`🚀 [${taskId}] 准备图片文件...`);
      console.log(`📁 [${taskId}] 当前图片URI:`, currentImageUri.substring(0, 50) + '...');
      
      // 处理最终图片：应用所有累积的变换
      let finalImageUri = currentImageUri;
      
      // 如果有旋转角度，一次性应用旋转
      if (rotation !== 0) {
        console.log(`🔄 [${taskId}] 应用最终旋转: ${rotation}°`);
        setIsProcessing(true);
        try {
          finalImageUri = await imageService.rotateImage(currentImageUri, rotation);
          console.log(`✅ [${taskId}] 最终旋转完成`);
        } catch (error) {
          console.error(`❌ [${taskId}] 最终旋转失败:`, error);
          Alert.alert('处理失败', `无法应用旋转: ${error instanceof Error ? error.message : '未知错误'}`);
          return;
        } finally {
          setIsProcessing(false);
        }
      }
      
      // 智能生成文件名和类型
      let fileName = 'image.jpg';
      let fileType = 'image/jpeg';
      
      if (finalImageUri.startsWith('data:')) {
        console.log(`🔍 [${taskId}] 检测到data URI，开始解析MIME类型...`);
        // 从data URI中提取MIME类型
        const mimeMatch = finalImageUri.match(/^data:([^;]+);/);
        if (mimeMatch) {
          fileType = mimeMatch[1];
          // 根据MIME类型设置正确的文件扩展名
          if (fileType === 'image/jpeg') {
            fileName = `${taskId}_image.jpg`;
          } else if (fileType === 'image/png') {
            fileName = `${taskId}_image.png`;
          } else if (fileType === 'image/gif') {
            fileName = `${taskId}_image.gif`;
          } else {
            fileName = `${taskId}_image.jpg`; // 默认使用jpg
          }
          console.log(`✅ [${taskId}] MIME类型解析: ${fileType}`);
        }
      } else {
        console.log(`🔍 [${taskId}] 处理文件路径URI...`);
        // 对于非data URI，尝试从路径中提取文件名
        const pathParts = finalImageUri.split('/');
        const lastPart = pathParts[pathParts.length - 1];
        if (lastPart && lastPart.includes('.')) {
          fileName = `${taskId}_${lastPart}`;
        } else {
          fileName = `${taskId}_image.jpg`;
        }
      }
      
      const file = {
        uri: finalImageUri,
        name: fileName,
        type: fileType,
      };
      console.log(`📦 [${taskId}] 准备传递给加载页面的文件:`, {
        name: file.name,
        type: file.type,
        uri: file.uri.substring(0, 50) + '...'
      });
      
      console.log(`🚀 [${taskId}] 跳转到加载页面开始批改...`);
      navigation.navigate('GradingLoading', {
        imageFile: file,
        taskId: taskId,
        imageUri: finalImageUri,
      });
    } catch (e: any) {
      console.error(`❌ [${taskId}] 上传/批改失败:`, e);
      Alert.alert('批改失败', `错误: ${e.message || '未知错误'}`);
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
      
      <ScrollView 
        key={`editor-scrollview-${scrollViewKey}`}
        style={styles.scrollView} 
        showsVerticalScrollIndicator={false}
        scrollEnabled={true}
        nestedScrollEnabled={false}
      >
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
                        { rotate: `${rotation % 360}deg` },
                        { scale: scaleAnim }
                      ],
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
                📐 旋转: {rotation % 360}°
              </Text>
              </View>
            </View>
          </View>

          {/* 控制面板 */}
          <View style={styles.controlsSection}>
            {/* 快速操作 */}
            <View style={styles.quickActions}>
              <View style={styles.decorativeButtonWrapper}>
                <DecorativeButton
                  onPress={handleRotate}
                  iconName="refresh"
                  size="md"
                  disabled={isProcessing}
                  gradientColors={['#FF9500', '#FF6B35']}
                  outerColor="#FFD60A"
                  borderColor="#FF8C00"
                />
                <Text style={styles.buttonLabel}>🔄 旋转</Text>
                <Text style={styles.buttonHint}>
                  {isProcessing ? '处理中...' : '点击旋转90°'}
                </Text>
              </View>
              
              <View style={styles.decorativeButtonWrapper}>
                <DecorativeButton
                  onPress={handleCrop}
                  iconName="crop"
                  size="md"
                  disabled={isProcessing}
                  gradientColors={['#34C759', '#30D158']}
                  outerColor="#A3F3BE"
                  borderColor="#00C851"
                />
                <Text style={styles.buttonLabel}>✂️ 裁剪</Text>
                <Text style={styles.buttonHint}>精确裁剪图片</Text>
              </View>
            </View>

            {/* 附加操作 */}
            <View style={styles.additionalActions}>
              <View style={styles.decorativeButtonWrapper}>
                <DecorativeButton
                  onPress={handleReset}
                  iconName="refresh-circle"
                  size="sm"
                  disabled={isProcessing}
                  gradientColors={['#8E8E93', '#6D6D70']}
                  outerColor="#D1D1D6"
                  borderColor="#8E8E93"
                />
                <Text style={styles.buttonLabel}>🔄 重置</Text>
              </View>
            </View>

            {/* 完成按钮 */}
            <View style={styles.completeButtonWrapper}>
              <DecorativeButton
                onPress={handleEditComplete}
                iconName="checkmark-circle"
                size="lg"
                gradientColors={['#007AFF', '#5856D6']}
                outerColor="#BF5AF2"
                borderColor="#AF52DE"
              />
              <Text style={styles.completeButtonText}>✨ 完成编辑</Text>
            </View>
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
    justifyContent: 'space-around',
    marginBottom: 32,
    gap: 16,
  },
  decorativeButtonWrapper: {
    alignItems: 'center',
    gap: 8,
    flex: 1,
  },
  buttonLabel: {
    color: textColor,
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
  buttonHint: {
    color: secondaryTextColor,
    fontSize: 12,
    textAlign: 'center',
    marginTop: 4,
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
  disabledButton: {
    opacity: 0.6,
  },
  additionalActions: {
    alignItems: 'center',
    marginBottom: 24,
  },
  completeButtonWrapper: {
    alignItems: 'center',
    gap: 12,
  },
  additionalActionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.05)',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: borderColor,
  },
  additionalActionIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  additionalActionText: {
    fontSize: 14,
    color: textColor,
    fontWeight: '600',
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
    color: textColor,
    fontSize: 18,
    fontWeight: '700',
    textAlign: 'center',
    marginTop: 8,
  },
});

export default ImageEditor; 