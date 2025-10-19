// 历史记录相关的类型定义

export interface HistoryRecord {
  id: string;                    // 唯一标识
  timestamp: number;             // 时间戳
  displayTime: string;           // 显示时间 "2024年1月15日 14:30"
  imageUri: string;              // 原始图片URI
  gradingResult: any;            // 完整批改结果
  wrongKnowledges?: any[];       // 错题知识点
  taskId: string;                // 任务ID
  summary?: {                    // 摘要信息，用于列表显示
    totalQuestions: number;      // 总题数
    correctCount: number;        // 正确题数
    wrongCount: number;          // 错误题数
    score?: number;              // 分数（可选）
  };
}

export interface HistoryFilters {
  startDate?: Date;              // 开始日期筛选
  endDate?: Date;                // 结束日期筛选
  searchText?: string;           // 搜索文本
  minCorrectRate?: number;       // 最低正确率 (0-100)
  maxCorrectRate?: number;       // 最高正确率 (0-100)
  minScore?: number;             // 最低分数筛选
  maxScore?: number;             // 最高分数筛选
  hasErrors?: boolean;           // 是否有错题
  questionCountRange?: {         // 题目数量范围
    min?: number;
    max?: number;
  };
}

export interface FilterPreset {
  id: string;
  name: string;
  filters: HistoryFilters;
  icon: string;
}

export interface DateRangePreset {
  id: string;
  name: string;
  getDateRange: () => { startDate: Date; endDate: Date };
}

export interface HistoryStats {
  totalRecords: number;          // 总记录数
  totalQuestions: number;        // 总题目数
  averageScore?: number;         // 平均分数（可选）
  recentActivity: Date | null;   // 最近活动时间
}
