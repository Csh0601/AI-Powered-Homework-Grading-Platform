import { HistoryRecord, HistoryStats } from '../types/HistoryTypes';
import historyService from './historyService';

export interface ExportData {
  version: string;
  exportDate: string;
  totalRecords: number;
  records: HistoryRecord[];
  statistics: HistoryStats;
  metadata: {
    appVersion: string;
    platform: string;
    deviceInfo?: string;
  };
}

export interface ExportOptions {
  format: 'json' | 'csv';
  includeImages: boolean;
  dateRange?: {
    startDate: Date;
    endDate: Date;
  };
  selectedRecords?: string[]; // 如果提供，只导出选中的记录
}

class DataExportService {
  private readonly EXPORT_VERSION = '1.0.0';
  private readonly APP_VERSION = '1.0.0'; // 应该从配置文件或构建信息获取

  // 导出历史记录
  async exportData(options: ExportOptions): Promise<string> {
    try {
      console.log('📤 开始导出数据:', options);
      
      let records = await historyService.getHistory();
      
      // 应用筛选条件
      if (options.selectedRecords && options.selectedRecords.length > 0) {
        records = records.filter(record => options.selectedRecords!.includes(record.id));
      }
      
      if (options.dateRange) {
        const { startDate, endDate } = options.dateRange;
        const startTime = startDate.getTime();
        const endTime = endDate.getTime() + 24 * 60 * 60 * 1000; // 加一天
        records = records.filter(record => 
          record.timestamp >= startTime && record.timestamp < endTime
        );
      }

      // 如果不包含图片，移除图片URI
      if (!options.includeImages) {
        records = records.map(record => ({
          ...record,
          imageUri: '', // 清空图片URI
        }));
      }

      const statistics = await historyService.getHistoryStats();
      
      const exportData: ExportData = {
        version: this.EXPORT_VERSION,
        exportDate: new Date().toISOString(),
        totalRecords: records.length,
        records,
        statistics,
        metadata: {
          appVersion: this.APP_VERSION,
          platform: 'React Native',
        },
      };

      if (options.format === 'json') {
        return this.exportAsJSON(exportData);
      } else if (options.format === 'csv') {
        return this.exportAsCSV(records);
      }

      throw new Error(`不支持的导出格式: ${options.format}`);
    } catch (error) {
      console.error('导出数据失败:', error);
      throw error;
    }
  }

  // 导出为JSON格式
  private exportAsJSON(data: ExportData): string {
    return JSON.stringify(data, null, 2);
  }

  // 导出为CSV格式
  private exportAsCSV(records: HistoryRecord[]): string {
    if (records.length === 0) {
      return 'timestamp,displayTime,taskId,totalQuestions,correctCount,wrongCount,score\n';
    }

    const headers = [
      'timestamp',
      'displayTime', 
      'taskId',
      'totalQuestions',
      'correctCount',
      'wrongCount',
      'score',
      'correctRate'
    ];

    const csvRows = [headers.join(',')];

    records.forEach(record => {
      const summary = record.summary || { totalQuestions: 0, correctCount: 0, wrongCount: 0 };
      const correctRate = summary.totalQuestions > 0 
        ? ((summary.correctCount / summary.totalQuestions) * 100).toFixed(1)
        : '0.0';

      const row = [
        record.timestamp.toString(),
        `"${record.displayTime}"`,
        `"${record.taskId}"`,
        summary.totalQuestions.toString(),
        summary.correctCount.toString(),
        summary.wrongCount.toString(),
        summary.score?.toString() || '',
        correctRate
      ];

      csvRows.push(row.join(','));
    });

    return csvRows.join('\n');
  }

  // 验证导入数据格式
  validateImportData(data: string): { isValid: boolean; error?: string; data?: ExportData } {
    try {
      const parsed = JSON.parse(data);
      
      // 检查必需字段
      if (!parsed.version) {
        return { isValid: false, error: '缺少版本信息' };
      }
      
      if (!parsed.records || !Array.isArray(parsed.records)) {
        return { isValid: false, error: '缺少有效的记录数据' };
      }

      // 检查版本兼容性
      if (parsed.version !== this.EXPORT_VERSION) {
        console.warn(`版本不匹配: 期望 ${this.EXPORT_VERSION}, 实际 ${parsed.version}`);
        // 这里可以添加版本兼容性处理逻辑
      }

      // 验证记录格式
      for (let i = 0; i < parsed.records.length; i++) {
        const record = parsed.records[i];
        if (!this.validateRecord(record)) {
          return { 
            isValid: false, 
            error: `第 ${i + 1} 条记录格式无效` 
          };
        }
      }

      return { isValid: true, data: parsed as ExportData };
    } catch (error) {
      return { 
        isValid: false, 
        error: `JSON解析失败: ${error instanceof Error ? error.message : '未知错误'}` 
      };
    }
  }

  // 验证单条记录格式
  private validateRecord(record: any): boolean {
    return (
      typeof record.id === 'string' &&
      typeof record.timestamp === 'number' &&
      typeof record.displayTime === 'string' &&
      typeof record.taskId === 'string' &&
      record.gradingResult &&
      (!record.summary || this.validateSummary(record.summary))
    );
  }

  // 验证摘要格式
  private validateSummary(summary: any): boolean {
    return (
      typeof summary.totalQuestions === 'number' &&
      typeof summary.correctCount === 'number' &&
      typeof summary.wrongCount === 'number' &&
      (summary.score === undefined || typeof summary.score === 'number')
    );
  }

  // 导入数据
  async importData(
    data: ExportData, 
    options: { 
      mergeMode: 'replace' | 'merge' | 'append';
      skipDuplicates: boolean;
    }
  ): Promise<{ success: boolean; imported: number; skipped: number; errors: string[] }> {
    try {
      console.log('📥 开始导入数据:', { recordCount: data.records.length, options });
      
      const existingRecords = await historyService.getHistory();
      const existingIds = new Set(existingRecords.map(r => r.id));
      
      let recordsToImport: HistoryRecord[] = [];
      let skipped = 0;
      const errors: string[] = [];

      // 处理记录
      for (const record of data.records) {
        if (options.skipDuplicates && existingIds.has(record.id)) {
          skipped++;
          continue;
        }

        // 生成新ID如果存在重复
        if (existingIds.has(record.id)) {
          record.id = `imported_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        }

        recordsToImport.push(record);
      }

      // 根据合并模式处理
      let finalRecords: HistoryRecord[] = [];
      
      switch (options.mergeMode) {
        case 'replace':
          finalRecords = recordsToImport;
          break;
        case 'merge':
          // 合并，新记录覆盖同ID的旧记录
          const mergedMap = new Map<string, HistoryRecord>();
          existingRecords.forEach(record => mergedMap.set(record.id, record));
          recordsToImport.forEach(record => mergedMap.set(record.id, record));
          finalRecords = Array.from(mergedMap.values());
          break;
        case 'append':
          finalRecords = [...existingRecords, ...recordsToImport];
          break;
      }

      // 按时间排序
      finalRecords.sort((a, b) => b.timestamp - a.timestamp);

      // 保存数据（这里需要直接操作AsyncStorage，因为historyService的方法是单条保存）
      // 为了简化，我们使用清空后批量添加的方式
      if (options.mergeMode === 'replace') {
        await historyService.clearAllHistory();
      }

      // 批量添加记录（需要修改historyService添加批量导入方法）
      // 暂时使用循环添加
      let imported = 0;
      for (const record of recordsToImport) {
        try {
          // 这里应该调用一个不触发缓存清除的内部保存方法
          // 暂时使用现有方法
          await this.importSingleRecord(record);
          imported++;
        } catch (error) {
          errors.push(`导入记录 ${record.id} 失败: ${error}`);
        }
      }

      console.log(`✅ 导入完成: 成功 ${imported} 条, 跳过 ${skipped} 条, 错误 ${errors.length} 条`);

      return {
        success: errors.length === 0,
        imported,
        skipped,
        errors,
      };
    } catch (error) {
      console.error('导入数据失败:', error);
      throw error;
    }
  }

  // 导入单条记录（简化版本，直接操作存储）
  private async importSingleRecord(record: HistoryRecord): Promise<void> {
    // 这里应该有一个更直接的方法来保存记录
    // 暂时使用historyService的方法，但这会影响性能
    const { imageUri, gradingResult, wrongKnowledges, taskId } = record;
    await historyService.saveHistory(imageUri, gradingResult, wrongKnowledges || [], taskId);
  }

  // 生成导出文件名
  generateFileName(format: 'json' | 'csv', prefix = 'homework_history'): string {
    const now = new Date();
    const dateStr = now.toISOString().split('T')[0]; // YYYY-MM-DD
    const timeStr = now.toTimeString().split(' ')[0].replace(/:/g, '-'); // HH-MM-SS
    
    return `${prefix}_${dateStr}_${timeStr}.${format}`;
  }

  // 计算导出数据大小
  calculateDataSize(records: HistoryRecord[], includeImages: boolean): number {
    const testExport: ExportData = {
      version: this.EXPORT_VERSION,
      exportDate: new Date().toISOString(),
      totalRecords: records.length,
      records: includeImages ? records : records.map(r => ({ ...r, imageUri: '' })),
      statistics: {
        totalRecords: records.length,
        totalQuestions: 0,
        averageScore: 0,
        recentActivity: null,
      },
      metadata: {
        appVersion: this.APP_VERSION,
        platform: 'React Native',
      },
    };

    return new Blob([JSON.stringify(testExport)]).size;
  }
}

export default new DataExportService();
