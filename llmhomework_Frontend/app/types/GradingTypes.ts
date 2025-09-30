// 批改系统数据类型定义 - 适配Qwen2.5-VL多模态服务

// 题目信息接口
export interface Question {
  number: string;           // 题号（如1、2、3等）
  stem: string;            // 题目内容
  answer: string;          // 学生答案
  type: string;            // 题目类型（选择题/填空题/计算题/应用题等）
  question_id: string;     // 题目唯一ID（自动生成如q_001、q_002等）
  similar_question?: string; // 相似的题目（新增字段）
}

// 批改结果接口
export interface GradingResult {
  question: string;                    // 题目内容
  answer: string;                      // 学生答案
  type: string;                        // 题目类型
  correct: boolean;                    // 是否正确
  score: number;                       // 得分
  explanation: string;                 // 详细说明（错误原因或正确要点）
  question_id: string;                 // 对应的题目ID
  knowledge_points: string[];          // 相关知识点列表
  correct_answer?: string;             // 正确答案（可选）
  learning_suggestions?: string[];     // 学习建议（新增字段）
  similar_question?: string;           // 相似的题目（新增字段）
}

// 批改总结接口
export interface GradingSummary {
  total_questions: number;             // 总题数
  correct_count: number;               // 正确题数
  total_score: number;                 // 总分
  accuracy_rate: number;               // 正确率
  main_issues: string[];               // 主要问题列表
  knowledge_points: string[];          // 涉及的所有知识点
  learning_suggestions?: string[];     // 学习建议（新增字段）
  similar_question?: string;           // 相似的题目（新增字段）
}

// 完整的API响应接口
export interface GradingResponse {
  questions: Question[];               // 识别的题目列表
  grading_result: GradingResult[];     // 批改结果列表
  summary: GradingSummary;             // 批改总结
  
  // 兼容旧格式的字段（标记为可选）
  isCorrect?: boolean;
  score?: number;
  type?: string;
  question?: string;
  userAnswer?: string;
  aiFeedback?: string;
  knowledgePoint?: string;
  questionId?: string;
}

// 题目类型枚举
export enum QuestionType {
  MULTIPLE_CHOICE = "选择题",
  FILL_BLANK = "填空题", 
  CALCULATION = "计算题",
  APPLICATION = "应用题",
  PROOF = "证明题",
  ANALYSIS = "分析题",
  COMPREHENSIVE = "综合题",
  OTHER = "其他"
}

// 知识点分类接口
export interface KnowledgePoint {
  name: string;                        // 知识点名称
  category?: string;                   // 知识点分类
  difficulty?: 'easy' | 'medium' | 'hard'; // 难度级别
}

// 错误分析接口
export interface ErrorAnalysis {
  type: string;                        // 错误类型
  description: string;                 // 错误描述
  suggestion: string;                  // 改进建议
  severity: 'low' | 'medium' | 'high'; // 严重程度
}

// 学习建议接口
export interface StudyRecommendation {
  knowledge_point: string;             // 相关知识点
  recommendation: string;              // 学习建议
  priority: 'low' | 'medium' | 'high'; // 优先级
  resources?: string[];                // 推荐资源
}

// 扩展的批改响应接口（包含分析和建议）
export interface EnhancedGradingResponse extends GradingResponse {
  error_analysis?: ErrorAnalysis[];    // 错误分析
  study_recommendations?: StudyRecommendation[]; // 学习建议
  knowledge_analysis?: {               // 知识点分析
    mastered: string[];                // 已掌握的知识点
    needs_improvement: string[];       // 需要改进的知识点
    suggestions: string[];             // 学习建议
  };
}

// API请求接口
export interface UploadRequest {
  file: {
    uri: string;
    name: string;
    type: string;
  };
  options?: {
    analyze_knowledge?: boolean;       // 是否进行知识点分析
    generate_suggestions?: boolean;    // 是否生成学习建议
    detailed_feedback?: boolean;       // 是否提供详细反馈
  };
}

// 向后兼容的数据转换工具
export class GradingDataAdapter {
  // 将新格式转换为旧格式（向后兼容）
  static toOldFormat(newData: GradingResponse): any {
    if (!newData.grading_result || newData.grading_result.length === 0) {
      return {
        isCorrect: false,
        score: 0,
        type: "未知",
        question: "无题目",
        userAnswer: "无答案",
        aiFeedback: "无反馈",
        knowledgePoint: "无",
        questionId: "unknown"
      };
    }

    const firstResult = newData.grading_result[0];
    return {
      isCorrect: firstResult.correct,
      score: firstResult.score,
      type: firstResult.type,
      question: firstResult.question,
      userAnswer: firstResult.answer,
      aiFeedback: firstResult.explanation,
      knowledgePoint: firstResult.knowledge_points.join(", "),
      questionId: firstResult.question_id
    };
  }

  // 检查是否为新格式数据
  static isNewFormat(data: any): data is GradingResponse {
    return data && 
           Array.isArray(data.questions) && 
           Array.isArray(data.grading_result) && 
           data.summary &&
           typeof data.summary.total_questions === 'number';
  }

  // 验证数据完整性
  static validateGradingResponse(data: any): string[] {
    const errors: string[] = [];
    
    if (!data) {
      errors.push("响应数据为空");
      return errors;
    }

    if (!Array.isArray(data.questions)) {
      errors.push("questions字段缺失或不是数组");
    }

    if (!Array.isArray(data.grading_result)) {
      errors.push("grading_result字段缺失或不是数组");
    }

    if (!data.summary) {
      errors.push("summary字段缺失");
    } else {
      if (typeof data.summary.total_questions !== 'number') {
        errors.push("summary.total_questions不是数字");
      }
      if (!Array.isArray(data.summary.main_issues)) {
        errors.push("summary.main_issues不是数组");
      }
      if (!Array.isArray(data.summary.knowledge_points)) {
        errors.push("summary.knowledge_points不是数组");
      }
    }

    return errors;
  }
}
