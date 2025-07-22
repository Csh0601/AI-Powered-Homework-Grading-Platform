export interface CorrectionResult {
  questionId: string;
  question: string; // 题目内容
  userAnswer: string;
  correctAnswer: string;
  isCorrect: boolean;
  knowledgePoint: string;
}
