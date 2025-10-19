import { RouteProp, useRoute, useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useEffect, useState, useRef, useCallback } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView, 
  Animated, 
  Alert,
  StatusBar,
  TouchableOpacity,
  BackHandler,
  Platform
} from 'react-native';
import { Gesture, GestureDetector, GestureHandlerRootView } from 'react-native-gesture-handler';
import Loader from '../components/Loader';
import { RootStackParamList } from '../navigation/NavigationTypes';
import {
  primaryColor,
  textPrimary,
  textSecondary,
  backgroundPrimary,
  cardBackground,
  errorColor,
  primaryAlpha10
} from '../styles/colors';
import { typography, spacing, borderRadius, shadows } from '../styles/designSystem';
import apiService from '../services/apiService';
import historyService from '../services/historyService';

type GradingLoadingRouteProp = RouteProp<RootStackParamList, 'GradingLoading'>;

const GradingLoadingScreen: React.FC = () => {
  const route = useRoute<GradingLoadingRouteProp>();
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  
  const { imageFile, taskId } = route.params;
  
  // 动画值
  const fadeValue = useRef(new Animated.Value(0)).current;
  const scaleValue = useRef(new Animated.Value(0.8)).current;
  const translateY = useRef(new Animated.Value(50)).current;
  
  // 状态管理
  const [, setIsProcessing] = useState(true);
  const [uploadProgress, setUploadProgress] = useState(0);
  const abortControllerRef = useRef<AbortController | null>(null);
  
  const startGradingProcess = useCallback(async () => {
    try {
      console.log(`\n=== 🚀 [${taskId}] 开始批改处理流程 ===`);
      console.log(`🚀 [${taskId}] 开始上传图片进行批改...`);
      
      // 创建AbortController用于取消请求
      abortControllerRef.current = new AbortController();
      
      // 模拟上传进度
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + Math.random() * 15;
        });
      }, 200);
      
      const result = await apiService.uploadImage(imageFile, abortControllerRef.current.signal);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      console.log(`🎉 [${taskId}] 后端批改完成!`);
      console.log(`📊 [${taskId}] 批改结果概览:`, {
        hasResult: !!result,
        hasGradingResult: !!(result?.grading_result),
        questionCount: result?.grading_result?.length || 0,
        taskId: (result as any)?.task_id || (result as any)?.taskId || 'unknown'
      });
      
      // 自动保存历史记录
      try {
        console.log(`💾 [${taskId}] 保存批改结果到历史记录...`);
        await historyService.saveHistory(
          imageFile.uri,
          result,
          (result as any)?.wrong_knowledges || [],
          taskId
        );
        console.log(`✅ [${taskId}] 历史记录保存成功`);
      } catch (saveError) {
        console.error(`❌ [${taskId}] 保存历史记录失败:`, saveError);
        // 不阻止正常流程，只记录错误
      }

      // 短暂延迟后跳转到结果页面
      setTimeout(() => {
        setIsProcessing(false);
        navigation.replace('Result', {
          gradingResult: result,
          wrongKnowledges: (result as any)?.wrong_knowledges || [],
          taskId: taskId,
          timestamp: (result as any)?.timestamp || Date.now(),
        });
      }, 500);
      
    } catch (error: any) {
      console.error(`❌ [${taskId}] 上传/批改失败:`, error);
      
      if (error.name === 'AbortError') {
        console.log(`🚫 [${taskId}] 用户取消了批改请求`);
        // 用户主动取消，不显示错误
        return;
      }
      
      setIsProcessing(false);
      Alert.alert(
        '批改失败', 
        `错误: ${error.message || '未知错误'}`,
        [
          {
            text: '重试',
            onPress: () => {
              setIsProcessing(true);
              setUploadProgress(0);
              startGradingProcess();
            }
          },
          {
            text: '返回',
            onPress: () => {
              console.log('🔄 批改失败，重置导航栈到Upload页面');
              navigation.reset({
                index: 0,
                routes: [{ name: 'Upload' }],
              });
            },
            style: 'cancel'
          }
        ]
      );
    }
  }, [imageFile, taskId, navigation]);

  const handleCancelGrading = useCallback(() => {
    console.log('🚫 用户请求取消批改');
    Alert.alert(
      '确认取消',
      '正在批改中，确定要取消吗？',
      [
        {
          text: '继续批改',
          style: 'cancel'
        },
        {
          text: '确定取消',
          style: 'destructive',
          onPress: () => {
            console.log('✅ 用户确认取消批改，开始清理和导航');
            if (abortControllerRef.current) {
              console.log('🛑 中止网络请求');
              abortControllerRef.current.abort();
            }
            setIsProcessing(false);
            // 重置导航栈，确保返回到Upload页面
            console.log('🔄 重置导航栈到Upload页面');
            navigation.reset({
              index: 0,
              routes: [{ name: 'Upload' }],
            });
          }
        }
      ]
    );
  }, [navigation]);

  useEffect(() => {
    // 页面进入动画
    Animated.parallel([
      Animated.timing(fadeValue, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.timing(scaleValue, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.timing(translateY, {
        toValue: 0,
        duration: 800,
        useNativeDriver: true,
      }),
    ]).start();

    // 不再需要旋转动画，新的Loader组件有自己的动画

    // Android 后退按钮处理
    const backHandler = Platform.OS === 'android' ? BackHandler.addEventListener(
      'hardwareBackPress',
      () => {
        console.log('📱 Android 后退按钮被按下');
        handleCancelGrading();
        return true; // 阻止默认的后退行为
      }
    ) : null;

    // 开始批改流程
    startGradingProcess();

    return () => {
      // spinAnimation不再需要，已移除
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (backHandler) {
        backHandler.remove();
      }
    };
  }, [fadeValue, scaleValue, translateY, startGradingProcess, handleCancelGrading]);

  // 左滑手势处理（适配 iOS 和 Android）
  const swipeGesture = Gesture.Pan()
    .minDistance(40) // 最小滑动距离
    .activeOffsetX([-120, 120]) // 水平激活区域，增大范围
    .failOffsetY([-80, 80]) // 垂直失效区域，避免与垂直滚动冲突
    .onStart(() => {
      console.log('🫴 [iOS/Android] 手势开始');
    })
    .onUpdate((event) => {
      // 实时输出手势信息用于调试（减少日志频率）
      if (Math.abs(event.translationX) > 50 && Math.abs(event.translationX) % 20 < 5) {
        console.log(`🫴 [${Platform.OS}] 手势更新: X=${event.translationX.toFixed(1)}, Y=${event.translationY.toFixed(1)}, VX=${event.velocityX.toFixed(1)}`);
      }
    })
    .onEnd((event) => {
      console.log(`🫴 [${Platform.OS}] 手势结束: X=${event.translationX.toFixed(1)}, Y=${event.translationY.toFixed(1)}, VX=${event.velocityX.toFixed(1)}`);
      
      // 检测向左滑动：translationX 为负值且绝对值足够大
      // 针对不同平台调整敏感度
      const minDistance = Platform.OS === 'ios' ? -80 : -100;
      const minVelocity = Platform.OS === 'ios' ? 300 : 400;
      const maxVertical = Platform.OS === 'ios' ? 120 : 150;
      
      if (event.translationX < minDistance && Math.abs(event.velocityX) > minVelocity && Math.abs(event.translationY) < maxVertical) {
        console.log(`✅ [${Platform.OS}] 检测到有效左滑手势，准备取消批改`);
        handleCancelGrading();
      } else {
        console.log(`❌ [${Platform.OS}] 手势不符合左滑条件: 距离=${event.translationX.toFixed(1)}, 速度=${event.velocityX.toFixed(1)}, 垂直=${event.translationY.toFixed(1)}`);
      }
    });

  // spin interpolation不再需要，已移除

  return (
    <GestureHandlerRootView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <StatusBar barStyle="dark-content" backgroundColor={backgroundPrimary} />

        <GestureDetector gesture={swipeGesture}>
          <View style={styles.gestureContainer}>
            {/* 顶部导航栏 - Apple 简洁风格 */}
            <View style={styles.navigationBar}>
              <View style={styles.navTitleContainer}>
                <Text style={styles.navTitle}>智能批改</Text>
                <Text style={styles.navSubtitle}>AI 批改中</Text>
              </View>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={handleCancelGrading}
              >
                <Text style={styles.cancelButtonText}>取消</Text>
              </TouchableOpacity>
            </View>

            {/* 主要内容区域 */}
            <Animated.View 
              style={[
                styles.contentContainer,
                {
                  opacity: fadeValue,
                  transform: [
                    { scale: scaleValue },
                    { translateY: translateY }
                  ]
                }
              ]}
            >
              {/* 加载动画区域 */}
              <View style={styles.loadingSection}>
                <View style={styles.loaderContainer}>
                  <Loader 
                    size={16} 
                    color={primaryColor} 
                    spacing={12} 
                  />
                </View>
                
                {/* 进度条 */}
                <View style={styles.progressContainer}>
                  <View style={styles.progressBar}>
                    <View 
                      style={[
                        styles.progressFill,
                        { width: `${uploadProgress}%` }
                      ]}
                    />
                  </View>
                  <Text style={styles.progressText}>
                    {Math.round(uploadProgress)}%
                  </Text>
                </View>
              </View>

              {/* 提示文字区域 - 克制简洁 */}
              <View style={styles.messageSection}>
                <Text style={styles.mainMessage}>
                  批改需要约 2-3 分钟
                </Text>
                <Text style={styles.subMessage}>
                  请耐心等待
                </Text>
              </View>

              {/* 底部提示 */}
              <View style={styles.hintSection}>
                {/* 备用取消按钮 */}
                <TouchableOpacity 
                  style={styles.emergencyCancel}
                  onPress={handleCancelGrading}
                  activeOpacity={0.7}
                >
                  <Text style={styles.emergencyCancelText}>点击取消</Text>
                </TouchableOpacity>
              </View>
            </Animated.View>
          </View>
        </GestureDetector>
      </SafeAreaView>
    </GestureHandlerRootView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: backgroundPrimary,
  },
  safeArea: {
    flex: 1,
  },
  gestureContainer: {
    flex: 1,
  },
  navigationBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.screenHorizontal,
    paddingVertical: spacing.lg,
    backgroundColor: cardBackground,
  },
  navTitleContainer: {
    flex: 1,
  },
  navTitle: {
    ...typography.heading2,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.xs / 2,
  },
  navSubtitle: {
    ...typography.bodySmall,
    color: textSecondary,
  },
  cancelButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.button,
    backgroundColor: primaryAlpha10,
  },
  cancelButtonText: {
    ...typography.buttonSmall,
    fontWeight: '500',
    color: primaryColor,
  },
  contentContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing.xxxl,
  },
  loadingSection: {
    alignItems: 'center',
    marginBottom: spacing.xxxl,
  },
  loaderContainer: {
    backgroundColor: cardBackground,
    paddingVertical: spacing.xl,
    paddingHorizontal: spacing.xxl,
    borderRadius: borderRadius.card,
    marginBottom: spacing.xxl,
    ...shadows.level3,
  },
  progressContainer: {
    alignItems: 'center',
    width: '100%',
  },
  progressBar: {
    width: '80%',
    height: 6,
    backgroundColor: primaryAlpha10,
    borderRadius: borderRadius.xs,
    overflow: 'hidden',
    marginBottom: spacing.sm,
  },
  progressFill: {
    height: '100%',
    backgroundColor: primaryColor,
    borderRadius: borderRadius.xs,
  },
  progressText: {
    ...typography.label,
    color: textSecondary,
  },
  messageSection: {
    alignItems: 'center',
    marginBottom: spacing.xxxl,
  },
  mainMessage: {
    ...typography.bodyLarge,
    fontWeight: '400',
    color: textPrimary,
    textAlign: 'center',
    marginBottom: spacing.xs,
  },
  subMessage: {
    ...typography.bodyMedium,
    color: textSecondary,
    textAlign: 'center',
  },
  hintSection: {
    position: 'absolute',
    bottom: 80,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  emergencyCancel: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: 'rgba(239, 68, 68, 0.3)',
  },
  emergencyCancelText: {
    ...typography.label,
    color: errorColor,
    textAlign: 'center',
  },
});

export default GradingLoadingScreen;