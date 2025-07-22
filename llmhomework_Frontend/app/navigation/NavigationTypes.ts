// 导航参数类型定义，供 createNativeStackNavigator 使用

export type RootStackParamList = {
  Upload: undefined;
  EditImage: { imageUri: string } | undefined;
  Result: { resultId?: string; gradingResult?: any[]; wrongKnowledges?: string[]; history?: any[] } | undefined;
  History: undefined;
};
