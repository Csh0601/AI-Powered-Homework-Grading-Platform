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
  textColor, 
  secondaryTextColor, 
  backgroundColor, 
  cardBackgroundColor,
  borderColor,
  systemGray6
} from '../styles/colors';
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
        <StatusBar barStyle="dark-content" backgroundColor={backgroundColor} />
        
        <GestureDetector gesture={swipeGesture}>
          <View style={styles.gestureContainer}>
            {/* 顶部导航栏 */}
            <View style={styles.navigationBar}>
              <View style={styles.navIconContainer}>
                <Text style={styles.navIcon}>📚</Text>
              </View>
              <Text style={styles.navTitle}>智能批改</Text>
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

              {/* 提示文字区域 */}
              <View style={styles.messageSection}>
                <Text style={styles.mainMessage}>
                  请耐心等待，批改的时间
                </Text>
                <Text style={styles.mainMessage}>
                  大概需要两到三分钟
                </Text>
                
                <View style={styles.emojiContainer}>
                  <Text style={styles.emoji}>😊</Text>
                  <Text style={styles.emoji}>🤖</Text>
                  <Text style={styles.emoji}>⏰</Text>
                </View>
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
    backgroundColor: backgroundColor,
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
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: cardBackgroundColor,
    borderBottomWidth: 1,
    borderBottomColor: borderColor,
  },
  navIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: primaryColor + '15',
    alignItems: 'center',
    justifyContent: 'center',
  },
  navIcon: {
    fontSize: 20,
  },
  navTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: textColor,
    flex: 1,
    textAlign: 'center',
    marginHorizontal: 16,
  },
  cancelButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 16,
    backgroundColor: systemGray6,
  },
  cancelButtonText: {
    fontSize: 14,
    fontWeight: '500',
    color: secondaryTextColor,
  },
  contentContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  loadingSection: {
    alignItems: 'center',
    marginBottom: 60,
  },
  loaderContainer: {
    backgroundColor: cardBackgroundColor,
    paddingVertical: 24,
    paddingHorizontal: 32,
    borderRadius: 20,
    marginBottom: 32,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 8,
    },
    shadowOpacity: 0.1,
    shadowRadius: 16,
    elevation: 8,
  },
  progressContainer: {
    alignItems: 'center',
    width: '100%',
  },
  progressBar: {
    width: '80%',
    height: 6,
    backgroundColor: systemGray6,
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressFill: {
    height: '100%',
    backgroundColor: primaryColor,
    borderRadius: 3,
  },
  progressText: {
    fontSize: 14,
    fontWeight: '500',
    color: secondaryTextColor,
  },
  messageSection: {
    alignItems: 'center',
    marginBottom: 60,
  },
  mainMessage: {
    fontSize: 18,
    fontWeight: '500',
    color: textColor,
    textAlign: 'center',
    lineHeight: 28,
  },
  emojiContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 24,
    gap: 16,
  },
  emoji: {
    fontSize: 32,
  },
  hintSection: {
    position: 'absolute',
    bottom: 80,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  emergencyCancel: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    backgroundColor: 'rgba(255, 59, 48, 0.1)',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 59, 48, 0.3)',
  },
  emergencyCancelText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FF3B30',
    textAlign: 'center',
  },
});

export default GradingLoadingScreen;