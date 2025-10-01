import { createNativeStackNavigator } from '@react-navigation/native-stack';
import React from 'react';
import EditImageScreen from '../screens/EditImageScreen';
import ExplanationScreen from '../screens/ExplanationScreen';
import GradingLoadingScreen from '../screens/GradingLoadingScreen';
import HistoryScreen from '../screens/HistoryScreen';
import HistoryDetailScreen from '../screens/HistoryDetailScreen';
import KnowledgePointsScreen from '../screens/KnowledgePointsScreen';
import ResultScreen from '../screens/ResultScreen';
import SimilarQuestionsScreen from '../screens/SimilarQuestionsScreen';
import StudySuggestionsScreen from '../screens/StudySuggestionsScreen';
import UploadScreen from '../screens/UploadScreen';
import ChatScreen from '../screens/ChatScreen';
import { RootStackParamList } from './NavigationTypes';

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function AppNavigator() {
  return (
    <Stack.Navigator initialRouteName="Upload">
      <Stack.Screen name="Upload" component={UploadScreen} options={{ title: '上传作业' }} />
      <Stack.Screen name="EditImage" component={EditImageScreen} options={{ title: '图片预处理' }} />
      <Stack.Screen 
        name="GradingLoading" 
        component={GradingLoadingScreen} 
        options={{ 
          title: '智能批改',
          headerShown: false // 隐藏默认头部，使用自定义导航栏
        }} 
      />
      <Stack.Screen name="Result" component={ResultScreen} options={{ title: '批改结果' }} />
      <Stack.Screen 
        name="History" 
        component={HistoryScreen} 
        options={{ 
          title: '历史记录',
          headerShown: false // 使用自定义导航栏
        }} 
      />
      <Stack.Screen 
        name="HistoryDetail" 
        component={HistoryDetailScreen} 
        options={{ 
          title: '批改详情',
          headerShown: false // 使用自定义导航栏
        }} 
      />
      <Stack.Screen name="Explanation" component={ExplanationScreen} options={{ title: '解析详情' }} />
      <Stack.Screen name="KnowledgePoints" component={KnowledgePointsScreen} options={{ title: '知识点详情' }} />
      <Stack.Screen name="StudySuggestions" component={StudySuggestionsScreen} options={{ title: '学习建议' }} />
      <Stack.Screen name="SimilarQuestions" component={SimilarQuestionsScreen} options={{ title: '相似的题目' }} />
      <Stack.Screen name="Chat" component={ChatScreen} options={{ title: 'AI学习伙伴' }} />
    </Stack.Navigator>
  );
}
