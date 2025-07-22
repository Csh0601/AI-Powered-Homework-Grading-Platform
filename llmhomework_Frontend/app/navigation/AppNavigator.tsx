import { createNativeStackNavigator } from '@react-navigation/native-stack';
import React from 'react';
import EditImageScreen from '../screens/EditImageScreen';
import HistoryScreen from '../screens/HistoryScreen';
import ResultScreen from '../screens/ResultScreen';
import UploadScreen from '../screens/UploadScreen';

export type RootStackParamList = {
  Upload: undefined;
  EditImage: { imageUri: string } | undefined;
  Result: { resultId: string } | undefined;
  History: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function AppNavigator() {
  return (
    <Stack.Navigator initialRouteName="Upload">
      <Stack.Screen name="Upload" component={UploadScreen} options={{ title: '上传作业' }} />
      <Stack.Screen name="EditImage" component={EditImageScreen} options={{ title: '图片预处理' }} />
      <Stack.Screen name="Result" component={ResultScreen} options={{ title: '批改结果' }} />
      <Stack.Screen name="History" component={HistoryScreen} options={{ title: '历史记录' }} />
    </Stack.Navigator>
  );
}
