import { RouteProp, useNavigation, useRoute } from '@react-navigation/native';
import React from 'react';
import { Alert, StyleSheet, View } from 'react-native';
import ImageEditor from '../components/ImageEditor';
import { RootStackParamList } from '../navigation/NavigationTypes';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';

// 定义路由类型

type EditImageScreenRouteProp = RouteProp<RootStackParamList, 'EditImage'>;

const EditImageScreen: React.FC = () => {
  const route = useRoute<EditImageScreenRouteProp>();
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  
  const imageUri = route.params?.imageUri;
  const taskId = route.params?.taskId || 'unknown_task';
  
  console.log(`\n=== 📷 [${taskId}] 进入图片编辑页面 ===`);
  console.log(`📷 [${taskId}] 接收到的route.params:`, JSON.stringify(route.params, null, 2));
  console.log(`📷 [${taskId}] 解析的imageUri:`, imageUri ? imageUri.substring(0, 50) + '...' : 'null');

  if (!imageUri) {
    console.log(`❌ [${taskId}] EditImageScreen: 未获取到图片URI`);
    Alert.alert('错误', '未获取到图片');
    navigation.goBack();
    return null;
  }
  
  console.log(`✅ [${taskId}] EditImageScreen: 图片URI有效，准备渲染ImageEditor`);

  return (
    <View style={styles.container}>
      <ImageEditor imageUri={imageUri} taskId={taskId} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
});

export default EditImageScreen;
