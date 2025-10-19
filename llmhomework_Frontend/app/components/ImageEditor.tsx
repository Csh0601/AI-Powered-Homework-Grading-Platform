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
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import apiService from '../services/apiService';
import imageService from '../services/imageService';
import ImageCropper from './ImageCropper';
import { IconButton } from './shared/IconButton';
import { RootStackParamList } from '../navigation/NavigationTypes';
import {
  primaryColor,
  successColor,
  textPrimary,
  textSecondary,
  backgroundPrimary,
  cardBackground,
  primaryAlpha10,
  textInverse
} from '../styles/colors';
import { typography, spacing, borderRadius, shadows, sizes } from '../styles/designSystem';

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
    
    // 先关闭裁剪器，清理手势状态
    setShowCropper(false);
    
    // 延迟更新图片URI和重置ScrollView，确保手势完全释放
    setTimeout(() => {
      setCurrentImageUri(croppedUri);
      setScrollViewKey(prev => prev + 1);
      console.log(`🔄 [${taskId}] 手势状态已清理，ScrollView已重新挂载，key: ${scrollViewKey + 1}`);
    }, 300); // 增加延迟到300ms，确保手势处理器完全释放
  };

  const handleCropCancel = () => {
    console.log(`❌ [${taskId}] 裁剪取消，返回ImageEditor`);
    
    // 先关闭裁剪器
    setShowCropper(false);
    
    // 延迟重置ScrollView，确保手势完全释放
    setTimeout(() => {
      setScrollViewKey(prev => prev + 1);
      console.log(`🔄 [${taskId}] 手势状态已清理，ScrollView已重新挂载，key: ${scrollViewKey + 1}`);
    }, 300); // 增加延迟到300ms
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
      <StatusBar barStyle="dark-content" backgroundColor={backgroundPrimary} />

      <ScrollView 
        key={`editor-scrollview-${scrollViewKey}`}
        style={styles.scrollView} 
        showsVerticalScrollIndicator={false}
        scrollEnabled={true}
        nestedScrollEnabled={false}
        keyboardShouldPersistTaps="handled"
        removeClippedSubviews={false}
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
          {/* 顶部导航栏 - Apple 风格 */}
          <View style={styles.navigationBar}>
            <Text style={styles.navTitle}>编辑图片</Text>
            <Text style={styles.navSubtitle}>调整后点击完成</Text>
          </View>

          {/* 图片预览区域 */}
          <View style={styles.imageSection}>
            <View style={styles.imageContainer}>
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
              <View style={styles.imageInfo}>
                <Ionicons name="sync-outline" size={14} color={primaryColor} style={{ marginRight: 4 }} />
                <Text style={styles.imageInfoText}>
                  旋转 {rotation % 360}°
                </Text>
              </View>
            </View>
          </View>

          {/* 控制面板 - iOS 底部工具栏风格 */}
          <View style={styles.controlsSection}>
            {/* 工具按钮行 */}
            <View style={styles.toolBar}>
              <View style={styles.toolButtonWrapper}>
                <IconButton
                  iconName="sync-outline"
                  onPress={handleRotate}
                  size="medium"
                  variant="ghost"
                  disabled={isProcessing}
                />
                <Text style={styles.toolButtonLabel}>旋转</Text>
              </View>

              <View style={styles.toolButtonWrapper}>
                <IconButton
                  iconName="crop-outline"
                  onPress={handleCrop}
                  size="medium"
                  variant="ghost"
                  disabled={isProcessing}
                />
                <Text style={styles.toolButtonLabel}>裁剪</Text>
              </View>

              <View style={styles.toolButtonWrapper}>
                <IconButton
                  iconName="refresh-outline"
                  onPress={handleReset}
                  size="medium"
                  variant="ghost"
                  disabled={isProcessing}
                />
                <Text style={styles.toolButtonLabel}>重置</Text>
              </View>
            </View>

            {/* 完成按钮 */}
            <TouchableOpacity
              style={styles.completeButton}
              onPress={handleEditComplete}
              disabled={isProcessing}
              activeOpacity={0.8}
            >
              <Text style={styles.completeButtonText}>完成</Text>
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
    backgroundColor: backgroundPrimary,
  },
  scrollView: {
    flex: 1,
  },
  container: {
    flex: 1,
    minHeight: '100%',
  },
  navigationBar: {
    paddingTop: spacing.xl,
    paddingBottom: spacing.lg,
    paddingHorizontal: spacing.screenHorizontal,
    alignItems: 'center',
  },
  navTitle: {
    ...typography.heading1,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.xs / 2,
    textAlign: 'center',
  },
  navSubtitle: {
    ...typography.bodySmall,
    color: textSecondary,
    textAlign: 'center',
  },
  imageSection: {
    paddingHorizontal: spacing.screenHorizontal,
    marginBottom: spacing.xl,
  },
  imageContainer: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.md,
    ...shadows.level3,
  },
  image: {
    width: '100%',
    height: 380,
    borderRadius: borderRadius.md,
  },
  imageInfo: {
    backgroundColor: primaryAlpha10,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.full,
    alignSelf: 'center',
    marginTop: spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
  },
  imageInfoText: {
    color: primaryColor,
    ...typography.caption,
    fontWeight: '500',
  },
  controlsSection: {
    paddingHorizontal: spacing.screenHorizontal,
    paddingBottom: spacing.xl,
  },

  // iOS 工具栏风格
  toolBar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: cardBackground,
    borderRadius: borderRadius.md,
    ...shadows.level1,
  },

  toolButtonWrapper: {
    alignItems: 'center',
    gap: spacing.xs,
  },

  toolButtonLabel: {
    ...typography.caption,
    color: textSecondary,
    fontWeight: '500',
  },

  // 完成按钮 - iOS 风格
  completeButton: {
    backgroundColor: primaryColor,
    height: sizes.button.large,
    borderRadius: borderRadius.button,
    alignItems: 'center',
    justifyContent: 'center',
    ...shadows.level2,
  },

  completeButtonText: {
    color: textInverse,
    ...typography.buttonLarge,
    fontWeight: '500',
  },
});

export default ImageEditor; 