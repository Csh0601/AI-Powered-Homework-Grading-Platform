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
  
  console.log('📷 EditImageScreen已加载');
  console.log('📷 接收到的route.params:', JSON.stringify(route.params, null, 2));
  
  const imageUri = route.params?.imageUri;
  console.log('📷 解析的imageUri:', imageUri);

  if (!imageUri) {
    console.log('❌ EditImageScreen: 未获取到图片URI');
    Alert.alert('错误', '未获取到图片');
    navigation.goBack();
    return null;
  }
  
  console.log('✅ EditImageScreen: 图片URI有效，准备渲染ImageEditor');

  // 修复：编辑完成后跳转到结果页面
  const handleEditComplete = (result: any) => {
    console.log('EditImageScreen收到结果:', JSON.stringify(result, null, 2));
    
    if (result && result.grading_result) {
      console.log('准备跳转到Result页面...');
      console.log('传递给Result的数据结构:', {
        gradingResult: result,  // 传递整个result对象
        wrongKnowledges: result.wrong_knowledges || [],
        taskId: result.task_id || 'unknown',
        timestamp: result.timestamp || Date.now(),
      });
      
      navigation.navigate('Result', {
        gradingResult: result,  // 传递整个result对象，而不是只传递grading_result数组
        wrongKnowledges: result.wrong_knowledges || [],
        taskId: result.task_id || 'unknown',
        timestamp: result.timestamp || Date.now(),
      });
    } else {
      console.error('批改结果格式错误，缺少grading_result字段:', result);
      Alert.alert('批改结果异常', `未能获取到批改结果。\n返回数据: ${JSON.stringify(result, null, 2)}`);
    }
  };

  return (
    <View style={styles.container}>
      <ImageEditor imageUri={imageUri} onEditComplete={handleEditComplete} />
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
