import AsyncStorage from '@react-native-async-storage/async-storage';
import { HistoryRecord, HistoryFilters, HistoryStats, FilterPreset, DateRangePreset } from '../types/HistoryTypes';

const HISTORY_KEY = 'grading_history';
const MAX_HISTORY_RECORDS = 100; // 最大保存100条记录
const CACHE_DURATION = 30000; // 缓存30秒

class HistoryService {
  private cache: {
    records: HistoryRecord[] | null;
    stats: HistoryStats | null;
    timestamp: number;
  } = {
    records: null,
    stats: null,
    timestamp: 0,
  };

  // 检查缓存是否有效
  private isCacheValid(): boolean {
    return Date.now() - this.cache.timestamp < CACHE_DURATION;
  }

  // 清除缓存
  private clearCache(): void {
    this.cache.records = null;
    this.cache.stats = null;
    this.cache.timestamp = 0;
  }

  // 更新缓存
  private updateCache(records: HistoryRecord[], stats?: HistoryStats): void {
    this.cache.records = records;
    this.cache.stats = stats || this.generateStatsFromRecords(records);
    this.cache.timestamp = Date.now();
  }

  // 从记录生成统计信息
  private generateStatsFromRecords(records: HistoryRecord[]): HistoryStats {
    if (records.length === 0) {
      return {
        totalRecords: 0,
        totalQuestions: 0,
        recentActivity: null,
      };
    }

    let totalQuestions = 0;

    records.forEach(record => {
      if (record.summary) {
        totalQuestions += record.summary.totalQuestions;
      }
    });

    const recentActivity = records.length > 0 ? new Date(records[0].timestamp) : null;

    return {
      totalRecords: records.length,
      totalQuestions,
      recentActivity,
    };
  }
  // 格式化显示时间
  private formatDisplayTime(timestamp: number): string {
    const date = new Date(timestamp);
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    
    return `${year}年${month}月${day}日 ${hours}:${minutes}`;
  }

  // 生成记录摘要
  private generateSummary(gradingResult: any): HistoryRecord['summary'] {
    try {
      if (!gradingResult || !gradingResult.grading_result) {
        console.warn('⚠️ 批改结果为空或缺少grading_result字段');
        return { totalQuestions: 0, correctCount: 0, wrongCount: 0 };
      }

      const results = Array.isArray(gradingResult.grading_result) 
        ? gradingResult.grading_result 
        : [];

      const totalQuestions = results.length;
      let correctCount = 0;
      let wrongCount = 0;

      console.log('🔍 分析批改结果:', results);

      results.forEach((result: any, index: number) => {
        console.log(`题目 ${index + 1}:`, {
          correct: result.correct,          // 新格式字段
          is_correct: result.is_correct,    // 旧格式字段
          type_correct: typeof result.correct,
          type_is_correct: typeof result.is_correct
        });

        // 支持新旧两种数据格式的正确判断逻辑
        // 优先使用新格式的 'correct' 字段，后备使用旧格式的 'is_correct' 字段
        const isCorrect = 
          // 新格式 (GradingTypes.ts 中的 correct 字段)
          result.correct === true || 
          result.correct === 'true' || 
          result.correct === 1 || 
          result.correct === '1' ||
          // 旧格式兼容 (is_correct 字段)
          result.is_correct === true || 
          result.is_correct === 'true' || 
          result.is_correct === 1 || 
          result.is_correct === '1';

        if (isCorrect) {
          correctCount++;
          console.log(`✅ 题目 ${index + 1} 判定为正确 (使用字段: ${result.correct !== undefined ? 'correct' : 'is_correct'})`);
        } else {
          wrongCount++;
          console.log(`❌ 题目 ${index + 1} 判定为错误 (使用字段: ${result.correct !== undefined ? 'correct' : 'is_correct'})`);
        }
      });

      const summary: HistoryRecord['summary'] = {
        totalQuestions,
        correctCount,
        wrongCount,
      };

      console.log('📊 生成摘要结果:', summary);
      console.log('📊 正确率:', totalQuestions > 0 ? (correctCount / totalQuestions * 100).toFixed(1) + '%' : '0%');
      return summary;
    } catch (error) {
      console.error('生成摘要时出错:', error);
      return { totalQuestions: 0, correctCount: 0, wrongCount: 0 };
    }
  }

  // 生成唯一ID
  private generateId(): string {
    return `history_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // 获取所有历史记录
  async getHistory(): Promise<HistoryRecord[]> {
    try {
      // 检查缓存
      if (this.isCacheValid() && this.cache.records) {
        console.log('📚 使用缓存数据');
        return this.cache.records;
      }

      console.log('📚 从存储加载数据');
      const data = await AsyncStorage.getItem(HISTORY_KEY);
      if (!data) {
        const emptyRecords: HistoryRecord[] = [];
        this.updateCache(emptyRecords);
        return emptyRecords;
      }
      
      const records: HistoryRecord[] = JSON.parse(data);
      // 按时间倒序排列（最新的在前）
      const sortedRecords = records.sort((a, b) => b.timestamp - a.timestamp);
      
      // 更新缓存
      this.updateCache(sortedRecords);
      
      return sortedRecords;
    } catch (error) {
      console.error('获取历史记录失败:', error);
      return [];
    }
  }

  // 保存新的历史记录
  async saveHistory(
    imageUri: string,
    gradingResult: any,
    wrongKnowledges: any[] = [],
    taskId: string
  ): Promise<HistoryRecord> {
    try {
      const timestamp = Date.now();
      const record: HistoryRecord = {
        id: this.generateId(),
        timestamp,
        displayTime: this.formatDisplayTime(timestamp),
        imageUri,
        gradingResult,
        wrongKnowledges,
        taskId,
        summary: this.generateSummary(gradingResult),
      };

      const existingRecords = await this.getHistory();
      const updatedRecords = [record, ...existingRecords];

      // 限制最大记录数，删除最老的记录
      if (updatedRecords.length > MAX_HISTORY_RECORDS) {
        updatedRecords.splice(MAX_HISTORY_RECORDS);
      }

      await AsyncStorage.setItem(HISTORY_KEY, JSON.stringify(updatedRecords));
      
      // 清除缓存，强制下次重新加载
      this.clearCache();
      
      console.log(`✅ 历史记录保存成功: ${record.displayTime}`);
      return record;
    } catch (error) {
      console.error('保存历史记录失败:', error);
      throw error;
    }
  }

  // 根据ID获取单条记录
  async getRecordById(id: string): Promise<HistoryRecord | null> {
    try {
      const records = await this.getHistory();
      return records.find(record => record.id === id) || null;
    } catch (error) {
      console.error('获取历史记录详情失败:', error);
      return null;
    }
  }

  // 删除单条记录
  async deleteRecord(id: string): Promise<boolean> {
    try {
      const records = await this.getHistory();
      const filteredRecords = records.filter(record => record.id !== id);
      
      if (filteredRecords.length === records.length) {
        return false; // 没有找到要删除的记录
      }

      await AsyncStorage.setItem(HISTORY_KEY, JSON.stringify(filteredRecords));
      
      // 清除缓存
      this.clearCache();
      
      console.log(`✅ 历史记录删除成功: ${id}`);
      return true;
    } catch (error) {
      console.error('删除历史记录失败:', error);
      return false;
    }
  }

  // 清空所有历史记录
  async clearAllHistory(): Promise<boolean> {
    try {
      await AsyncStorage.removeItem(HISTORY_KEY);
      
      // 清除缓存
      this.clearCache();
      
      console.log('✅ 所有历史记录已清空');
      return true;
    } catch (error) {
      console.error('清空历史记录失败:', error);
      return false;
    }
  }

  // 获取历史统计信息
  async getHistoryStats(): Promise<HistoryStats> {
    try {
      // 检查缓存
      if (this.isCacheValid() && this.cache.stats) {
        console.log('📊 使用缓存统计数据');
        return this.cache.stats;
      }

      console.log('📊 重新计算统计数据');
      const records = await this.getHistory();
      
      // 如果 getHistory 已经更新了缓存，直接使用缓存的统计数据
      if (this.cache.stats) {
        return this.cache.stats;
      }

      // 否则重新生成统计数据
      const stats = this.generateStatsFromRecords(records);
      this.cache.stats = stats;
      
      return stats;
    } catch (error) {
      console.error('获取历史统计失败:', error);
      return {
        totalRecords: 0,
        totalQuestions: 0,
        recentActivity: null,
      };
    }
  }

  // 根据筛选条件获取记录
  async getFilteredHistory(filters: HistoryFilters): Promise<HistoryRecord[]> {
    try {
      let records = await this.getHistory();

      // 日期筛选
      if (filters.startDate) {
        const startTimestamp = filters.startDate.getTime();
        records = records.filter(record => record.timestamp >= startTimestamp);
      }

      if (filters.endDate) {
        const endTimestamp = filters.endDate.getTime() + 24 * 60 * 60 * 1000; // 加一天
        records = records.filter(record => record.timestamp < endTimestamp);
      }

      // 文本搜索（搜索任务ID和显示时间）
      if (filters.searchText && filters.searchText.trim()) {
        const searchLower = filters.searchText.toLowerCase().trim();
        records = records.filter(record => 
          record.displayTime.toLowerCase().includes(searchLower) ||
          record.taskId.toLowerCase().includes(searchLower)
        );
      }


      // 正确率范围筛选
      if (filters.minCorrectRate !== undefined || filters.maxCorrectRate !== undefined) {
        records = records.filter(record => {
          if (!record.summary || record.summary.totalQuestions === 0) return false;
          const correctRate = (record.summary.correctCount / record.summary.totalQuestions) * 100;
          if (filters.minCorrectRate !== undefined && correctRate < filters.minCorrectRate) return false;
          if (filters.maxCorrectRate !== undefined && correctRate > filters.maxCorrectRate) return false;
          return true;
        });
      }

      // 是否有错题筛选
      if (filters.hasErrors !== undefined) {
        records = records.filter(record => {
          const hasErrors = record.summary && record.summary.wrongCount > 0;
          return filters.hasErrors ? hasErrors : !hasErrors;
        });
      }

      // 题目数量范围筛选
      if (filters.questionCountRange) {
        const { min, max } = filters.questionCountRange;
        records = records.filter(record => {
          if (!record.summary) return false;
          const count = record.summary.totalQuestions;
          if (min !== undefined && count < min) return false;
          if (max !== undefined && count > max) return false;
          return true;
        });
      }

      return records;
    } catch (error) {
      console.error('筛选历史记录失败:', error);
      return [];
    }
  }

  // 获取筛选预设
  getFilterPresets(): FilterPreset[] {
    return [
      {
        id: 'all_correct',
        name: '全对记录',
        icon: '✅',
        filters: { minCorrectRate: 100 }
      },
      {
        id: 'has_errors',
        name: '有错题',
        icon: '❌',
        filters: { hasErrors: true }
      },
      {
        id: 'recent_week',
        name: '最近一周',
        icon: '📅',
        filters: { 
          startDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
          endDate: new Date()
        }
      },
      {
        id: 'many_questions',
        name: '题目较多',
        icon: '📚',
        filters: { questionCountRange: { min: 5 } }
      }
    ];
  }

  // 获取日期范围预设
  getDateRangePresets(): DateRangePreset[] {
    return [
      {
        id: 'today',
        name: '今天',
        getDateRange: () => {
          const today = new Date();
          today.setHours(0, 0, 0, 0);
          const tomorrow = new Date(today);
          tomorrow.setDate(tomorrow.getDate() + 1);
          return { startDate: today, endDate: tomorrow };
        }
      },
      {
        id: 'week',
        name: '最近一周',
        getDateRange: () => {
          const endDate = new Date();
          const startDate = new Date(endDate.getTime() - 7 * 24 * 60 * 60 * 1000);
          return { startDate, endDate };
        }
      },
      {
        id: 'month',
        name: '最近一月',
        getDateRange: () => {
          const endDate = new Date();
          const startDate = new Date();
          startDate.setMonth(startDate.getMonth() - 1);
          return { startDate, endDate };
        }
      },
      {
        id: 'quarter',
        name: '最近三月',
        getDateRange: () => {
          const endDate = new Date();
          const startDate = new Date();
          startDate.setMonth(startDate.getMonth() - 3);
          return { startDate, endDate };
        }
      }
    ];
  }

  // 修复现有历史记录的摘要数据
  async fixExistingRecords(): Promise<{ fixed: number; errors: string[] }> {
    try {
      console.log('🔧 开始修复现有历史记录的摘要数据...');
      const records = await this.getHistory();
      let fixedCount = 0;
      const errors: string[] = [];

      for (const record of records) {
        try {
          // 重新生成摘要
          const newSummary = this.generateSummary(record.gradingResult);
          
          // 检查是否需要修复
          const oldSummary = record.summary || { totalQuestions: 0, correctCount: 0, wrongCount: 0 };
          const needsFix = newSummary && (
            oldSummary.correctCount !== newSummary.correctCount ||
            oldSummary.wrongCount !== newSummary.wrongCount ||
            oldSummary.totalQuestions !== newSummary.totalQuestions
          );

          if (needsFix) {
            console.log(`🔧 修复记录 ${record.id}:`, {
              old: oldSummary,
              new: newSummary
            });
            
            record.summary = newSummary;
            fixedCount++;
          }
        } catch (error) {
          const errorMsg = `修复记录 ${record.id} 失败: ${error}`;
          console.error(errorMsg);
          errors.push(errorMsg);
        }
      }

      if (fixedCount > 0) {
        // 保存修复后的数据
        await AsyncStorage.setItem(HISTORY_KEY, JSON.stringify(records));
        this.clearCache(); // 清除缓存
        console.log(`✅ 修复完成: ${fixedCount} 条记录已修复`);
      } else {
        console.log('ℹ️ 没有需要修复的记录');
      }

      return { fixed: fixedCount, errors };
    } catch (error) {
      console.error('修复历史记录失败:', error);
      throw error;
    }
  }

  // 检查历史数据健康状况
  async checkDataHealth(): Promise<{
    totalRecords: number;
    healthyRecords: number;
    problematicRecords: number;
    issues: Array<{
      recordId: string;
      displayTime: string;
      issue: string;
    }>;
  }> {
    try {
      const records = await this.getHistory();
      const issues: Array<{ recordId: string; displayTime: string; issue: string }> = [];
      let healthyCount = 0;

      console.log('🔍 检查历史数据健康状况...');

      records.forEach(record => {
        let hasIssue = false;

        // 检查摘要是否存在
        if (!record.summary) {
          issues.push({
            recordId: record.id,
            displayTime: record.displayTime,
            issue: '缺少摘要信息'
          });
          hasIssue = true;
        } else {
          // 检查摘要数据一致性
          const { totalQuestions, correctCount, wrongCount } = record.summary;
          
          if (totalQuestions !== correctCount + wrongCount) {
            issues.push({
              recordId: record.id,
              displayTime: record.displayTime,
              issue: `题目数量不一致: 总数${totalQuestions} ≠ 正确${correctCount} + 错误${wrongCount}`
            });
            hasIssue = true;
          }

          if (totalQuestions === 0 && record.gradingResult && record.gradingResult.grading_result) {
            const actualQuestionCount = Array.isArray(record.gradingResult.grading_result) 
              ? record.gradingResult.grading_result.length 
              : 0;
            if (actualQuestionCount > 0) {
              issues.push({
                recordId: record.id,
                displayTime: record.displayTime,
                issue: `有${actualQuestionCount}道题的批改结果但摘要中总题数为0`
              });
              hasIssue = true;
            }
          }

          // 检查正确率是否合理
          const correctRate = totalQuestions > 0 ? (correctCount / totalQuestions) : 0;
          if (correctRate < 0 || correctRate > 1) {
            issues.push({
              recordId: record.id,
              displayTime: record.displayTime,
              issue: `正确率异常: ${(correctRate * 100).toFixed(1)}%`
            });
            hasIssue = true;
          }
        }

        if (!hasIssue) {
          healthyCount++;
        }
      });

      const result = {
        totalRecords: records.length,
        healthyRecords: healthyCount,
        problematicRecords: issues.length,
        issues
      };

      console.log('📊 数据健康状况:', result);
      return result;
    } catch (error) {
      console.error('检查数据健康状况失败:', error);
      throw error;
    }
  }
}

// 导出单例实例
export default new HistoryService();