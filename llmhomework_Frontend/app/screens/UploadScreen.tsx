import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import React, { useState, useCallback } from 'react';
import {
  Alert,
  StyleSheet,
  View,
  Text,
  SafeAreaView,
  StatusBar,
  ActionSheetIOS,
  Platform,
  ScrollView,
  TouchableOpacity,
  Animated,
  Dimensions
} from 'react-native';
import { RootStackParamList } from '../navigation/NavigationTypes';
import {
  primaryColor,
  textPrimary,
  textSecondary,
  backgroundPrimary,
  primaryAlpha10,
  cardBackground,
  textInverse
} from '../styles/colors';
import { typography, spacing, borderRadius, shadows } from '../styles/designSystem';

type UploadScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Upload'>;

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

const UploadScreen: React.FC = () => {
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string>('');
  const navigation = useNavigation<UploadScreenNavigationProp>();
  const [scaleAnim] = useState(new Animated.Value(0.95));
  const [fadeAnim] = useState(new Animated.Value(0));

  // 每次页面获得焦点时生成新的任务ID（但不清空图片）
  useFocusEffect(
    useCallback(() => {
      const newTaskId = `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setTaskId(newTaskId);
      console.log('\n=== 🎯 开始新题目处理 ===');
      console.log('🆔 题目任务ID:', newTaskId);
      console.log('📍 当前页面: UploadScreen');
      console.log('========================\n');

      // 启动动画
      Animated.parallel([
        Animated.spring(scaleAnim, {
          toValue: 1,
          tension: 40,
          friction: 7,
          useNativeDriver: true,
        }),
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 600,
          useNativeDriver: true,
        }),
      ]).start();

      return () => {
        console.log(`🔚 任务 ${newTaskId} 离开UploadScreen`);
      };
    }, [])
  );

  console.log(`📱 [${taskId}] UploadScreen 渲染，图片状态:`, imageUri ? '已选择' : '未选择');

  // 从相册选择图片
  const handlePickImage = async () => {
    try {
      console.log(`📱 [${taskId}] 开始选择图片...`);

      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        console.log(`❌ [${taskId}] 相册权限被拒绝`);
        Alert.alert('权限不足', '请允许访问相册');
        return;
      }

      console.log(`✅ [${taskId}] 相册权限获取成功，打开相册...`);

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        quality: 1,
        allowsEditing: false,
      });

      console.log(`📱 [${taskId}] 图片选择结果:`, result.canceled ? '用户取消' : '选择成功');

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const selectedImageUri = result.assets[0].uri;
        console.log(`✅ [${taskId}] 图片选择成功! URI: ${selectedImageUri.substring(0, 50)}...`);
        setImageUri(selectedImageUri);

        console.log(`🚀 [${taskId}] 图片选择成功，直接导航到编辑页面...`);
        navigation.navigate('EditImage', { imageUri: selectedImageUri, taskId });
        console.log(`✅ [${taskId}] 成功导航到编辑页面`);
      } else {
        console.log(`⏭️ [${taskId}] 用户取消了图片选择`);
      }
    } catch (error) {
      console.error(`❌ [${taskId}] 图片选择出错:`, error);
      Alert.alert('错误', '图片选择失败，请重试');
    }
  };

  // 显示图片来源选择器
  const handleImageSourceSelection = () => {
    console.log(`📱 [${taskId}] 显示图片来源选择器...`);

    if (Platform.OS === 'ios') {
      ActionSheetIOS.showActionSheetWithOptions(
        {
          options: ['取消', '拍照', '从相册选择'],
          cancelButtonIndex: 0,
        },
        (buttonIndex) => {
          if (buttonIndex === 1) {
            handleTakePhoto();
          } else if (buttonIndex === 2) {
            handlePickImage();
          }
        }
      );
    } else {
      Alert.alert(
        '选择图片来源',
        '请选择获取图片的方式',
        [
          { text: '取消', style: 'cancel' },
          { text: '拍照', onPress: handleTakePhoto },
          { text: '从相册选择', onPress: handlePickImage },
        ]
      );
    }
  };

  // 拍照
  const handleTakePhoto = async () => {
    try {
      console.log(`📷 [${taskId}] 开始拍照...`);

      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        console.log(`❌ [${taskId}] 相机权限被拒绝`);
        Alert.alert('权限不足', '请允许访问相机');
        return;
      }

      console.log(`✅ [${taskId}] 相机权限获取成功，打开相机...`);

      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ['images'],
        quality: 1,
        allowsEditing: false,
      });

      console.log(`📷 [${taskId}] 拍照结果:`, result.canceled ? '用户取消' : '拍照成功');

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const photoUri = result.assets[0].uri;
        console.log(`✅ [${taskId}] 拍照成功! URI: ${photoUri.substring(0, 50)}...`);
        setImageUri(photoUri);

        console.log(`🚀 [${taskId}] 拍照成功，直接导航到编辑页面...`);
        navigation.navigate('EditImage', { imageUri: photoUri, taskId });
        console.log(`✅ [${taskId}] 成功导航到编辑页面`);
      } else {
        console.log(`⏭️ [${taskId}] 用户取消了拍照`);
      }
    } catch (error) {
      console.error(`❌ [${taskId}] 拍照出错:`, error);
      Alert.alert('错误', '拍照失败，请重试');
    }
  };

  // 导航到历史记录
  const handleNavigateToHistory = () => {
    console.log(`📚 [${taskId}] 导航到历史记录页面`);
    try {
      navigation.navigate('History');
      console.log(`✅ [${taskId}] 成功导航到历史记录页面`);
    } catch (error) {
      console.error(`❌ [${taskId}] 导航到历史记录失败:`, error);
      Alert.alert('错误', `导航失败: ${error}`);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor={backgroundPrimary} />

      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.contentContainer}
        showsVerticalScrollIndicator={false}
      >
        <Animated.View
          style={[
            styles.animatedContainer,
            {
              opacity: fadeAnim,
              transform: [{ scale: scaleAnim }],
            },
          ]}
        >
          {/* 顶部标题区域 - Apple 极简风格 */}
          <View style={styles.headerSection}>
            <Text style={styles.appTitle}>智学伴</Text>
            <Text style={styles.appSubtitle}>AI 智能作业批改助手</Text>
          </View>

          {/* 主要功能区域 */}
          <View style={styles.actionsSection}>

            {/* 上传作业卡片 - iOS 风格 */}
            <TouchableOpacity
              style={styles.primaryActionCard}
              onPress={handleImageSourceSelection}
              activeOpacity={0.8}
            >
              <View style={styles.primaryActionIconContainer}>
                <Ionicons name="camera-outline" size={28} color={textInverse} />
              </View>
              <View style={styles.primaryActionContent}>
                <Text style={styles.primaryActionTitle}>拍照或选择图片</Text>
                <Text style={styles.primaryActionDescription}>
                  上传作业照片，开始智能批改
                </Text>
              </View>
              <View style={styles.arrowContainer}>
                <Ionicons name="chevron-forward" size={24} color={textInverse} />
              </View>
            </TouchableOpacity>

            {/* 历史记录卡片 - iOS 风格 */}
            <TouchableOpacity
              style={styles.secondaryActionCard}
              onPress={handleNavigateToHistory}
              activeOpacity={0.8}
            >
              <View style={styles.secondaryActionIconContainer}>
                <Ionicons name="time-outline" size={24} color={primaryColor} />
              </View>
              <View style={styles.secondaryActionContent}>
                <Text style={styles.secondaryActionTitle}>历史记录</Text>
                <Text style={styles.secondaryActionDescription}>
                  查看批改记录和学习数据
                </Text>
              </View>
              <View style={styles.arrowContainer}>
                <Ionicons name="chevron-forward" size={20} color={primaryColor} />
              </View>
            </TouchableOpacity>

            {/* 生成试卷卡片 - iOS 风格 */}
            <TouchableOpacity
              style={styles.secondaryActionCard}
              onPress={() => navigation.navigate('GeneratePaper')}
              activeOpacity={0.8}
            >
              <View style={styles.secondaryActionIconContainer}>
                <Ionicons name="document-text-outline" size={24} color={primaryColor} />
              </View>
              <View style={styles.secondaryActionContent}>
                <Text style={styles.secondaryActionTitle}>生成试卷</Text>
                <Text style={styles.secondaryActionDescription}>
                  从历史记录生成PDF练习试卷
                </Text>
              </View>
              <View style={styles.arrowContainer}>
                <Ionicons name="chevron-forward" size={20} color={primaryColor} />
              </View>
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

  container: {
    flex: 1,
  },

  contentContainer: {
    paddingHorizontal: spacing.screenHorizontal,
    paddingBottom: spacing.xxxl,
  },

  animatedContainer: {
    width: '100%',
  },

  // 顶部标题区域 - Apple 极简风格
  headerSection: {
    alignItems: 'center',
    paddingTop: spacing.xxxl + spacing.xl,
    paddingBottom: spacing.xxxl,
  },

  appTitle: {
    ...typography.displayMedium,
    fontWeight: '300',
    color: textPrimary,
    marginBottom: spacing.sm,
    textAlign: 'center',
    letterSpacing: -1,
  },

  appSubtitle: {
    ...typography.bodyMedium,
    color: textSecondary,
    textAlign: 'center',
  },

  // 主要功能区域
  actionsSection: {
    marginBottom: spacing.xl,
  },

  primaryActionCard: {
    backgroundColor: primaryColor,
    borderRadius: borderRadius.button,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    flexDirection: 'row',
    alignItems: 'center',
    ...shadows.level2,
  },

  primaryActionIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },

  primaryActionContent: {
    flex: 1,
  },

  primaryActionTitle: {
    ...typography.heading4,
    fontWeight: '500',
    color: textInverse,
    marginBottom: spacing.xs,
  },

  primaryActionDescription: {
    ...typography.bodySmall,
    color: 'rgba(255, 255, 255, 0.8)',
  },

  arrowContainer: {
    marginLeft: spacing.sm,
  },

  secondaryActionCard: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.button,
    padding: spacing.lg,
    flexDirection: 'row',
    alignItems: 'center',
    ...shadows.level1,
    borderWidth: 1,
    borderColor: primaryColor,
  },

  secondaryActionIconContainer: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: primaryAlpha10,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },

  secondaryActionContent: {
    flex: 1,
  },

  secondaryActionTitle: {
    ...typography.heading4,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.xs,
  },

  secondaryActionDescription: {
    ...typography.bodySmall,
    color: textSecondary,
  },
});

export default UploadScreen;