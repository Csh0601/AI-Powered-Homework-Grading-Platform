import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import * as ImagePicker from 'expo-image-picker';
import React, { useState, useCallback } from 'react';
import { Alert, StyleSheet, View, Text, SafeAreaView, StatusBar, ActionSheetIOS, Platform } from 'react-native';
import { RootStackParamList } from '../navigation/NavigationTypes';
import { DecorativeButton } from '../components/DecorativeButton';

type UploadScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Upload'>;

const UploadScreen: React.FC = () => {
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string>('');
  const navigation = useNavigation<UploadScreenNavigationProp>();

  // 每次页面获得焦点时生成新的任务ID（但不清空图片）
  useFocusEffect(
    useCallback(() => {
      const newTaskId = `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setTaskId(newTaskId);
      console.log('\n=== 🎯 开始新题目处理 ===');
      console.log('🆔 题目任务ID:', newTaskId);
      console.log('📍 当前页面: UploadScreen');
      console.log('========================\n');
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
      
      // 请求权限
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        console.log(`❌ [${taskId}] 相册权限被拒绝`);
        Alert.alert('权限不足', '请允许访问相册');
        return;
      }

      console.log(`✅ [${taskId}] 相册权限获取成功，打开相册...`);

      // 选择图片
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
        
        // 直接导航到编辑页面
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
      // Android使用Alert
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
      
      // 请求权限
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        console.log(`❌ [${taskId}] 相机权限被拒绝`);
        Alert.alert('权限不足', '请允许访问相机');
        return;
      }

      console.log(`✅ [${taskId}] 相机权限获取成功，打开相机...`);

      // 拍照
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
        
        // 直接导航到编辑页面
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
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />
      
      <Text style={styles.title}>AI作业批改系统</Text>
      
      {/* 操作按钮 */}
      <View style={styles.buttonContainer}>
        <View style={styles.decorativeButtonWrapper}>
          <DecorativeButton
            onPress={handleImageSourceSelection}
            iconName="camera"
            size="lg"
            gradientColors={['#007AFF', '#5856D6']}
            outerColor="#FFD60A"
            borderColor="#FF9500"
          />
          <Text style={styles.buttonLabel}>📸 拍照/选择图片</Text>
        </View>
        
        <View style={styles.decorativeButtonWrapper}>
          <DecorativeButton
            onPress={handleNavigateToHistory}
            iconName="library"
            size="lg"
            gradientColors={['#5856D6', '#AF52DE']}
            outerColor="#34C759"
            borderColor="#30D158"
          />
          <Text style={styles.buttonLabel}>📚 历史记录</Text>
        </View>
      </View>


      {/* 调试信息 */}
      <View style={styles.debugContainer}>
        <Text style={styles.debugText}>
          调试信息: {imageUri ? `已选择图片 (${imageUri.length} 字符)` : '未选择图片'}
        </Text>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 40,
    color: '#333',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 30,
    paddingHorizontal: 20,
  },
  decorativeButtonWrapper: {
    alignItems: 'center',
    gap: 12,
  },
  buttonLabel: {
    color: '#333',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
    maxWidth: 120,
  },
  debugContainer: {
    marginTop: 20,
    padding: 15,
    backgroundColor: '#e8e8e8',
    borderRadius: 8,
  },
  debugText: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
});

export default UploadScreen;