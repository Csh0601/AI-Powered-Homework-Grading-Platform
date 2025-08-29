// 导航参数类型定义，供 createNativeStackNavigator 使用

export type RootStackParamList = {
  Upload: undefined;
  EditImage: { imageUri: string };
  Result: { 
    resultId?: string; 
    gradingResult?: any; // 改为 any 类型以匹配传递的数据结构
    wrongKnowledges?: any[]; // 改为 any[] 类型
    history?: any[];
    taskId?: string;
    timestamp?: number;
  };
  History: undefined;
};
