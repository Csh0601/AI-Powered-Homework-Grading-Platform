import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import * as ImagePicker from 'expo-image-picker';
import React, { useState } from 'react';
import { Alert, Image, StyleSheet, View, TouchableOpacity, Text, SafeAreaView, StatusBar } from 'react-native';
import { RootStackParamList } from '../navigation/NavigationTypes';

type UploadScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Upload'>;

const UploadScreen: React.FC = () => {
  const [imageUri, setImageUri] = useState<string | null>(null);
  const navigation = useNavigation<UploadScreenNavigationProp>();

  console.log('🔄 UploadScreen 渲染，当前 imageUri:', imageUri);

  // 从相册选择图片
  const handlePickImage = async () => {
    try {
      console.log('📱 开始选择图片...');
      
      // 请求权限
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('权限不足', '请允许访问相册');
        return;
      }

      // 选择图片
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        quality: 1,
        allowsEditing: false,
      });

      console.log('📱 图片选择结果:', result);

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const selectedImageUri = result.assets[0].uri;
        console.log('📱 设置图片 URI:', selectedImageUri);
        setImageUri(selectedImageUri);
      } else {
        console.log('📱 用户取消了图片选择');
      }
    } catch (error) {
      console.error('📱 图片选择出错:', error);
      Alert.alert('错误', '图片选择失败，请重试');
    }
  };

  // 拍照
  const handleTakePhoto = async () => {
    try {
      console.log('📷 开始拍照...');
      
      // 请求权限
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('权限不足', '请允许访问相机');
        return;
      }

      // 拍照
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ['images'],
        quality: 1,
        allowsEditing: false,
      });

      console.log('📷 拍照结果:', result);

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const photoUri = result.assets[0].uri;
        console.log('📷 设置拍照 URI:', photoUri);
        setImageUri(photoUri);
      } else {
        console.log('📷 用户取消了拍照');
      }
    } catch (error) {
      console.error('📷 拍照出错:', error);
      Alert.alert('错误', '拍照失败，请重试');
    }
  };

  // 导航到编辑页面
  const handleNavigateToEdit = () => {
    console.log('🚀 handleNavigateToEdit 被调用');
    console.log('🚀 当前 imageUri:', imageUri);
    
    if (!imageUri) {
      console.log('❌ 没有图片，显示警告');
      Alert.alert('提示', '请先选择图片');
      return;
    }

    console.log('🚀 准备导航到 EditImage 页面...');
    console.log('🚀 导航参数:', { imageUri });
    
    try {
      navigation.navigate('EditImage', { imageUri });
      console.log('🚀 导航调用成功');
    } catch (error) {
      console.error('❌ 导航失败:', error);
      Alert.alert('错误', `导航失败: ${error}`);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />
      
      <Text style={styles.title}>AI作业批改系统</Text>
      
      {/* 操作按钮 */}
      <View style={styles.buttonContainer}>
        <TouchableOpacity 
          style={[styles.button, styles.primaryButton]} 
          onPress={handlePickImage}
        >
          <Text style={styles.buttonText}>📱 选择图片</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.button, styles.secondaryButton]} 
          onPress={handleTakePhoto}
        >
          <Text style={styles.buttonText}>📷 拍照</Text>
        </TouchableOpacity>
      </View>

      {/* 图片预览 */}
      {imageUri && (
        <View style={styles.previewContainer}>
          <Text style={styles.previewTitle}>图片预览</Text>
          <Image source={{ uri: imageUri }} style={styles.previewImage} />
          
          {/* 导航按钮 */}
          <TouchableOpacity 
            style={styles.navigateButton}
            onPress={handleNavigateToEdit}
          >
            <Text style={styles.navigateButtonText}>开始编辑 →</Text>
          </TouchableOpacity>
          
          {/* 测试按钮 */}
          <TouchableOpacity 
            style={styles.testButton}
            onPress={() => {
              console.log('🧪 测试按钮被点击');
              Alert.alert('测试', '按钮点击正常！');
            }}
          >
            <Text style={styles.testButtonText}>测试按钮</Text>
          </TouchableOpacity>
        </View>
      )}

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
    gap: 15,
    marginBottom: 30,
  },
  button: {
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderRadius: 10,
    alignItems: 'center',
  },
  primaryButton: {
    backgroundColor: '#007AFF',
  },
  secondaryButton: {
    backgroundColor: '#34C759',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  previewContainer: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  previewTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    textAlign: 'center',
    color: '#333',
  },
  previewImage: {
    width: '100%',
    height: 200,
    borderRadius: 10,
    marginBottom: 20,
  },
  navigateButton: {
    backgroundColor: '#FF6B35',
    paddingVertical: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 10,
  },
  navigateButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  testButton: {
    backgroundColor: '#8E8E93',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  testButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
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