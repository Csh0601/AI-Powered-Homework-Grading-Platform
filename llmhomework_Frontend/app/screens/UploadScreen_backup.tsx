// 备份原始文件 - 2025-08-29
// 备份原因：导航功能异常，需要重写
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import * as ImagePicker from 'expo-image-picker';
import React, { useState, useEffect } from 'react';
import { Alert, Image, StyleSheet, View, TouchableOpacity, Text, SafeAreaView, Animated, Dimensions, StatusBar } from 'react-native';
import { RootStackParamList } from '../navigation/NavigationTypes';
import { 
  primaryColor, 
  successColor, 
  textColor, 
  secondaryTextColor, 
  backgroundColor, 
  cardBackgroundColor,
  borderColor,
  secondaryColor,
  warningColor
} from '../styles/colors';

const { width: screenWidth } = Dimensions.get('window');

type UploadScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Upload'>;

const UploadScreen: React.FC = () => {
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [fadeAnim] = useState(new Animated.Value(0));
  const [scaleAnim] = useState(new Animated.Value(0.8));

  // 监控imageUri变化
  useEffect(() => {
    console.log('🖼️ imageUri状态变化:', imageUri);
    console.log('🖼️ imageUri类型:', typeof imageUri);
    console.log('🖼️ imageUri长度:', imageUri ? imageUri.length : 'null');
    
    if (imageUri) {
      console.log('🖼️ 图片URI已设置，应该显示预览区域');
      console.log('🖼️ 准备启动预览动画...');
      // 触发预览动画
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 500,
          useNativeDriver: true,
        }),
        Animated.timing(scaleAnim, {
          toValue: 1,
          duration: 500,
          useNativeDriver: true,
        }),
      ]).start(() => {
        console.log('🖼️ 预览动画完成，按钮应该可见');
      });
    } else {
      console.log('🖼️ 图片URI为空，不显示预览区域');
    }
  }, [imageUri]);
  const [slideAnim] = useState(new Animated.Value(30));
  const navigation = useNavigation<UploadScreenNavigationProp>();

  useEffect(() => {
    // 启动动画
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 50,
        friction: 7,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 600,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  // 拍照
  const handleTakePhoto = async () => {
    try {
      console.log('开始请求相机权限...');
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      console.log('相机权限状态:', status);
      
      if (status !== 'granted') {
        Alert.alert('权限不足', '请允许访问相机');
        return;
      }
      
      console.log('启动相机...');
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ['images'],
        quality: 1,
        allowsEditing: false,
      });
      
      console.log('拍照结果:', result);
      
      if (!result.canceled && result.assets && result.assets.length > 0) {
        const photoUri = result.assets[0].uri;
        console.log('设置拍照URI:', photoUri);
        setImageUri(photoUri);
        console.log('拍照完成，等待用户点击"开始编辑"按钮');
      } else {
        console.log('用户取消了拍照或拍照失败');
      }
    } catch (error) {
      console.error('拍照过程中出错:', error);
      Alert.alert('错误', '拍照失败，请重试');
    }
  };

  // 从相册选择
  const handlePickImage = async () => {
    try {
      console.log('开始请求相册权限...');
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      console.log('权限状态:', status);
      
      if (status !== 'granted') {
        Alert.alert('权限不足', '请允许访问相册');
        return;
      }
      
      console.log('启动图片选择器...');
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        quality: 1,
        allowsEditing: false, // 添加这个选项
      });
      
      console.log('图片选择结果:', result);
      
      if (!result.canceled && result.assets && result.assets.length > 0) {
        const selectedImageUri = result.assets[0].uri;
        console.log('设置图片URI:', selectedImageUri);
        setImageUri(selectedImageUri);
        console.log('图片设置完成，等待用户点击"开始编辑"按钮');
      } else {
        console.log('用户取消了图片选择或没有选择图片');
      }
    } catch (error) {
      console.error('图片选择过程中出错:', error);
      Alert.alert('错误', '图片选择失败，请重试');
    }
  };

  // 跳转到图片编辑页面
  const handleNext = () => {
    console.log('🔘 用户点击了"开始编辑"按钮');
    console.log('🔘 当前imageUri:', imageUri);
    
    if (imageUri) {
      console.log('🔘 准备跳转到EditImage页面...');
      console.log('🔘 导航参数:', { imageUri });
      try {
        navigation.navigate('EditImage', { imageUri });
        console.log('🔘 navigation.navigate调用完成');
      } catch (error) {
        console.error('❌ 导航失败:', error);
        Alert.alert('导航错误', `跳转失败: ${error}`);
      }
    } else {
      console.log('❌ 没有选择图片，显示警告');
      Alert.alert('请先选择图片');
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
              { scale: scaleAnim },
              { translateY: slideAnim }
            ]
          }
        ]}
      >
        {/* 顶部欢迎区域 */}
        <View style={styles.welcomeSection}>
          <View style={styles.logoContainer}>
            <View style={styles.logoCircle}>
              <Text style={styles.logoText}>📚</Text>
            </View>
            <View style={styles.logoGlow} />
          </View>
          <Text style={styles.welcomeTitle}>欢迎使用智能作业批改</Text>
          <Text style={styles.welcomeSubtitle}>上传您的作业图片，获得智能批改结果</Text>
          
          {/* 功能特性展示 */}
          <View style={styles.featuresContainer}>
            <View style={styles.featureItem}>
              <Text style={styles.featureIcon}>🤖</Text>
              <Text style={styles.featureText}>AI智能识别</Text>
            </View>
            <View style={styles.featureItem}>
              <Text style={styles.featureIcon}>⚡</Text>
              <Text style={styles.featureText}>快速批改</Text>
            </View>
            <View style={styles.featureItem}>
              <Text style={styles.featureIcon}>📊</Text>
              <Text style={styles.featureText}>详细分析</Text>
            </View>
          </View>
        </View>

        {/* 操作按钮区域 */}
        <View style={styles.actionSection}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionIcon}>📤</Text>
            <Text style={styles.sectionTitle}>选择上传方式</Text>
          </View>
          
          <View style={styles.actionButtons}>
            <TouchableOpacity 
              style={[styles.actionButton, styles.cameraButton]} 
              onPress={handleTakePhoto}
              activeOpacity={0.9}
            >
              <View style={styles.buttonIconContainer}>
                <Text style={styles.buttonIcon}>📷</Text>
              </View>
              <Text style={styles.actionButtonText}>拍照上传</Text>
              <Text style={styles.actionButtonSubtext}>使用相机拍摄作业</Text>
              <View style={styles.buttonArrow}>
                <Text style={styles.arrowText}>→</Text>
              </View>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.actionButton, styles.galleryButton]} 
              onPress={handlePickImage}
              activeOpacity={0.9}
            >
              <View style={styles.buttonIconContainer}>
                <Text style={styles.buttonIcon}>🖼️</Text>
              </View>
              <Text style={styles.actionButtonText}>相册选择</Text>
              <Text style={styles.actionButtonSubtext}>选择已保存的图片</Text>
              <View style={styles.buttonArrow}>
                <Text style={styles.arrowText}>→</Text>
              </View>
            </TouchableOpacity>
          </View>
        </View>

        {/* 图片预览区域 */}
        {imageUri ? (
          <Animated.View 
            style={[
              styles.previewSection,
              {
                opacity: fadeAnim,
                transform: [{ scale: scaleAnim }]
              }
            ]}
          >
            <View style={styles.previewContainer}>
              <View style={styles.previewHeader}>
                <View style={styles.previewTitleContainer}>
                  <Text style={styles.previewIcon}>🖼️</Text>
                  <Text style={styles.previewTitle}>图片预览</Text>
                </View>
                <View style={styles.previewBadge}>
                  <Text style={styles.previewBadgeText}>✓ 已选择</Text>
                </View>
              </View>
              
              <View style={styles.imagePreviewWrapper}>
                <Image source={{ uri: imageUri }} style={styles.imagePreview} />
                <View style={styles.imagePreviewBorder} />
              </View>
              
              <TouchableOpacity 
                style={[styles.nextButton, { backgroundColor: '#34C759' }]} 
                onPress={() => {
                  console.log('🔘 开始编辑按钮被点击了！');
                  console.log('🔘 当前时间:', new Date().toISOString());
                  console.log('🔘 按钮onPress事件触发');
                  handleNext();
                }}
                activeOpacity={0.9}
              >
                <Text style={styles.nextButtonText}>🎨 开始编辑 (点我测试)</Text>
              </TouchableOpacity>
              
              {/* 额外测试按钮 */}
              <TouchableOpacity 
                style={[styles.nextButton, { backgroundColor: '#FF6B35', marginTop: 10 }]} 
                onPress={() => {
                  console.log('🧪 测试按钮被点击！');
                  Alert.alert('测试', '这是一个测试按钮，确认可以点击！');
                }}
                activeOpacity={0.9}
              >
                <Text style={styles.nextButtonText}>🧪 测试按钮</Text>
              </TouchableOpacity>
            </View>
          </Animated.View>
        ) : (
          <View style={{ padding: 20 }}>
            <Text style={{ textAlign: 'center', color: '#666' }}>
              🔍 调试：imageUri = {String(imageUri)}
            </Text>
          </View>
        )}
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
    height: 400,
    backgroundColor: 'rgba(0, 122, 255, 0.04)',
    borderBottomLeftRadius: 120,
    borderBottomRightRadius: 120,
  },
  container: {
    flex: 1,
    paddingHorizontal: 20,
  },
  welcomeSection: {
    alignItems: 'center',
    paddingTop: 40,
    paddingBottom: 40,
  },
  logoContainer: {
    marginBottom: 24,
    position: 'relative',
  },
  logoCircle: {
    width: 90,
    height: 90,
    borderRadius: 45,
    backgroundColor: 'rgba(0, 122, 255, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 3,
    borderColor: 'rgba(0, 122, 255, 0.3)',
    shadowColor: primaryColor,
    shadowOffset: {
      width: 0,
      height: 8,
    },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  logoGlow: {
    position: 'absolute',
    top: -10,
    left: -10,
    right: -10,
    bottom: -10,
    borderRadius: 55,
    backgroundColor: 'rgba(0, 122, 255, 0.1)',
    zIndex: -1,
  },
  logoText: {
    fontSize: 40,
  },
  welcomeTitle: {
    fontSize: 32,
    fontWeight: '800',
    color: textColor,
    textAlign: 'center',
    marginBottom: 12,
    letterSpacing: -0.5,
  },
  welcomeSubtitle: {
    fontSize: 16,
    color: secondaryTextColor,
    textAlign: 'center',
    lineHeight: 24,
    fontWeight: '500',
    marginBottom: 32,
  },
  featuresContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    paddingHorizontal: 20,
  },
  featureItem: {
    alignItems: 'center',
    flex: 1,
  },
  featureIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  featureText: {
    fontSize: 12,
    color: secondaryTextColor,
    fontWeight: '600',
    textAlign: 'center',
  },
  actionSection: {
    marginBottom: 32,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
    justifyContent: 'center',
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
  actionButtons: {
    gap: 16,
  },
  actionButton: {
    backgroundColor: cardBackgroundColor,
    paddingVertical: 24,
    paddingHorizontal: 24,
    borderRadius: 20,
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
    position: 'relative',
  },
  cameraButton: {
    borderColor: primaryColor,
    borderWidth: 2,
  },
  galleryButton: {
    borderColor: secondaryColor,
    borderWidth: 2,
  },
  buttonIconContainer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'rgba(0, 122, 255, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
    alignSelf: 'center',
  },
  buttonIcon: {
    fontSize: 28,
  },
  actionButtonText: {
    fontSize: 18,
    fontWeight: '700',
    color: textColor,
    textAlign: 'center',
    marginBottom: 8,
  },
  actionButtonSubtext: {
    fontSize: 14,
    color: secondaryTextColor,
    textAlign: 'center',
    lineHeight: 20,
  },
  buttonArrow: {
    position: 'absolute',
    right: 20,
    top: '50%',
    marginTop: -15,
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: 'rgba(0, 122, 255, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  arrowText: {
    fontSize: 16,
    color: primaryColor,
    fontWeight: 'bold',
  },
  previewSection: {
    marginBottom: 20,
  },
  previewContainer: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 24,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 8,
    },
    shadowOpacity: 0.12,
    shadowRadius: 20,
    elevation: 8,
    borderWidth: 1,
    borderColor: 'rgba(0, 0, 0, 0.03)',
  },
  previewHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  previewTitleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  previewIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  previewTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: textColor,
  },
  previewBadge: {
    backgroundColor: 'rgba(52, 199, 89, 0.1)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(52, 199, 89, 0.2)',
  },
  previewBadgeText: {
    fontSize: 12,
    fontWeight: '600',
    color: successColor,
  },
  imagePreviewWrapper: {
    position: 'relative',
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 20,
    backgroundColor: backgroundColor,
  },
  imagePreview: {
    width: '100%',
    height: 200,
    borderRadius: 16,
  },
  imagePreviewBorder: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    borderWidth: 2,
    borderColor: 'rgba(0, 122, 255, 0.2)',
    borderRadius: 16,
    pointerEvents: 'none',
  },
  nextButton: {
    backgroundColor: successColor,
    paddingVertical: 18,
    paddingHorizontal: 32,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: successColor,
    shadowOffset: {
      width: 0,
      height: 6,
    },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 6,
  },
  nextButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '700',
  },
});

export default UploadScreen;
