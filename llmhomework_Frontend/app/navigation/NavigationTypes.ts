// 导航参数类型定义，供 createNativeStackNavigator 使用

export type RootStackParamList = {
  Upload: undefined;
  EditImage: { imageUri: string; taskId?: string };
  GradingLoading: { 
    imageFile: any; 
    taskId: string; 
    imageUri: string;
  };
  Result: { 
    resultId?: string; 
    gradingResult?: any; // 改为 any 类型以匹配传递的数据结构
    wrongKnowledges?: any[]; // 改为 any[] 类型
    history?: any[];
    taskId?: string;
    timestamp?: number;
  };
  History: undefined;
  HistoryDetail: { 
    recordId: string;
  };
  Explanation: {
    result: any;
  };
  KnowledgePoints: {
    knowledgePoints: string[];
    wrongKnowledges?: any[];
    knowledgeAnalysis?: {
      wrong_knowledge_points?: string[];
      study_recommendations?: string[];
    };
    gradingResult?: any[]; // 传递完整的批改结果以便提取learning_suggestions
  };
  StudySuggestions: {
    suggestions: string[];
    practiceQuestions?: any[];
    learningSuggestions?: string[]; // 新增：来自grading_result的学习建议
    summaryLearningSuggestions?: string[]; // 新增：来自summary的学习建议
  };
  SimilarQuestions: {
    questions: Array<{
      questionId: string;
      originalQuestion: string;
      similarQuestion: string;
      type?: string;
    }>;
  };
  Chat: {
    taskId: string;
    gradingResult: any;
  };
};
