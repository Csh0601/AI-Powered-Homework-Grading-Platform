export interface CorrectionResult {
  questionId: string;
  question: string; // 题目内容
  userAnswer: string;
  correctAnswer: string;
  isCorrect: boolean;
  knowledgePoint: string;
  explanation?: string; // 解释说明
  score?: number; // 得分
  type?: string; // 题目类型
}
