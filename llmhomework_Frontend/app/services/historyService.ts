import AsyncStorage from '@react-native-async-storage/async-storage';
import type { CorrectionResult } from '../models/CorrectionResult';

const HISTORY_KEY = 'correction_history';

const historyService = {
  // 保存一条历史记录（数组）
  async saveRecord(result: CorrectionResult[]) {
    try {
      const history = await historyService.loadHistory();
      const newRecord = {
        id: Date.now().toString(),
        date: new Date().toLocaleString(),
        summary: `共${result.length}题，正确${result.filter(r => r.isCorrect).length}题`,
        items: result,
      };
      const newHistory = [newRecord, ...history];
      await AsyncStorage.setItem(HISTORY_KEY, JSON.stringify(newHistory));
    } catch (e) {
      throw new Error('保存历史记录失败');
    }
  },

  // 加载所有历史记录
  async loadHistory() {
    try {
      const data = await AsyncStorage.getItem(HISTORY_KEY);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      throw new Error('加载历史记录失败');
    }
  },
};

export default historyService;
