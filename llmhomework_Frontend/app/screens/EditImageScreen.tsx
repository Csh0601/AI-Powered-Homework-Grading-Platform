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

  if (!imageUri) {
    Alert.alert('错误', '未获取到图片');
    navigation.goBack();
    return null;
  }

  // 修复：编辑完成后跳转到结果页面
  const handleEditComplete = (result: any) => {
    if (result && result.grading_result) {
      navigation.navigate('Result', {
        gradingResult: result.grading_result,
        wrongKnowledges: result.wrong_knowledges,
      });
    } else {
      Alert.alert('批改结果异常', '未能获取到批改结果，无法跳转');
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
