/**
 * 试卷生成服务
 * 处理试卷生成、预览和下载相关的API调用
 */

import axios from 'axios';
import * as FileSystem from 'expo-file-system/legacy';
import * as Sharing from 'expo-sharing';
import { Platform, Alert } from 'react-native';
import { API_CONFIG, getApiUrl } from '../config/api';

export interface PaperStatistics {
  total_records: number;
  total_similar_questions: number;
  can_generate: boolean;
  recommended_count: number;
}

export interface PaperQuestion {
  question: string;
  similar_question?: string;
  type?: string;
  source?: string;
  content?: string;
  text?: string;
}

export interface PaperPreview {
  questions: PaperQuestion[];
  total_found: number;
  will_use: number;
  message: string;
}

export interface GeneratePaperOptions {
  userId?: string;
  maxQuestions?: number;
  title?: string;
}

class PaperService {
  private baseURL: string;

  constructor() {
    this.baseURL = getApiUrl();
  }

  /**
   * 获取试卷统计信息
   */
  async getStatistics(userId?: string): Promise<PaperStatistics> {
    try {
      console.log('📊 获取试卷统计信息...');
      
      const url = `${this.baseURL}/api/paper/statistics${userId ? `?user_id=${userId}` : ''}`;
      
      const response = await axios.get<{
        success: boolean;
        statistics: PaperStatistics;
        error?: string;
      }>(url, {
        timeout: 10000,
        headers: {
          'Accept': 'application/json',
        }
      });

      if (response.data.success) {
        console.log('✅ 获取统计信息成功:', response.data.statistics);
        return response.data.statistics;
      } else {
        throw new Error(response.data.error || '获取统计信息失败');
      }
    } catch (error: any) {
      console.error('❌ 获取统计信息失败:', error);
      throw new Error(error.response?.data?.error || error.message || '网络请求失败');
    }
  }

  /**
   * 预览试卷内容（不生成PDF）
   */
  async previewPaper(options: GeneratePaperOptions = {}): Promise<PaperPreview> {
    try {
      console.log('👀 预览试卷内容...');
      
      const url = `${this.baseURL}/api/paper/preview`;
      
      const requestData = {
        user_id: options.userId,
        max_questions: options.maxQuestions || 10,
      };

      const response = await axios.post<{
        success: boolean;
        questions: PaperQuestion[];
        total_found: number;
        will_use: number;
        message: string;
        error?: string;
      }>(url, requestData, {
        timeout: 15000,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        }
      });

      if (response.data.success) {
        console.log('✅ 预览成功:', response.data.message);
        return {
          questions: response.data.questions,
          total_found: response.data.total_found,
          will_use: response.data.will_use,
          message: response.data.message,
        };
      } else {
        throw new Error(response.data.error || '预览失败');
      }
    } catch (error: any) {
      console.error('❌ 预览失败:', error);
      throw new Error(error.response?.data?.error || error.message || '网络请求失败');
    }
  }

  /**
   * 生成并下载试卷PDF
   */
  async generateAndDownloadPaper(options: GeneratePaperOptions = {}): Promise<string> {
    try {
      console.log('📝 开始生成试卷PDF...');
      
      const url = `${this.baseURL}/api/paper/generate`;
      
      const requestData = {
        user_id: options.userId,
        max_questions: options.maxQuestions || 10,
        title: options.title || '练习试卷',
      };

      console.log('📤 发送请求:', requestData);

      // 生成唯一的文件名
      const timestamp = new Date().getTime();
      const filename = `exam_paper_${timestamp}.pdf`;
      const fileUri = `${FileSystem.documentDirectory}${filename}`;

      console.log('📁 将保存到:', fileUri);

      // 使用fetch获取PDF数据
      console.log('🔄 使用fetch方式下载...');
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Accept': 'application/pdf',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        let errorMsg = '生成试卷失败';
        try {
          const errorData = await response.json();
          errorMsg = errorData.error || errorMsg;
        } catch (e) {
          errorMsg = `服务器错误: ${response.status}`;
        }
        throw new Error(errorMsg);
      }

      // 获取blob数据
      const blob = await response.blob();
      
      // 转换为base64
      const reader = new FileReader();
      const base64Data = await new Promise<string>((resolve, reject) => {
        reader.onloadend = () => {
          const base64 = (reader.result as string).split(',')[1];
          resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });

      // 写入文件
      await FileSystem.writeAsStringAsync(fileUri, base64Data, {
        encoding: FileSystem.EncodingType.Base64,
      });

      console.log('✅ PDF下载成功:', fileUri);
      
      // 检查是否支持分享
      const isAvailable = await Sharing.isAvailableAsync();
      if (isAvailable) {
        console.log('📤 打开分享对话框...');
        await Sharing.shareAsync(fileUri, {
          mimeType: 'application/pdf',
          dialogTitle: '保存试卷PDF',
          UTI: 'com.adobe.pdf',
        });
      } else {
        console.log('ℹ️ 当前平台不支持分享功能');
        Alert.alert(
          '下载成功',
          `试卷已保存到: ${fileUri}`,
          [{ text: '确定' }]
        );
      }

      return fileUri;

    } catch (error: any) {
      console.error('❌ 生成下载试卷失败:', error);
      
      // 详细错误信息
      if (error.response) {
        // 服务器返回错误
        const errorMsg = error.response.data?.error || error.message;
        throw new Error(errorMsg);
      } else if (error.request) {
        // 请求发送但没有收到响应
        throw new Error('服务器无响应，请检查网络连接');
      } else {
        // 其他错误
        throw new Error(error.message || '未知错误');
      }
    }
  }

  /**
   * 检查试卷生成服务健康状态
   */
  async healthCheck(): Promise<boolean> {
    try {
      const url = `${this.baseURL}/api/paper/health`;
      
      const response = await axios.get<{
        status: string;
      }>(url, {
        timeout: 5000,
      });

      return response.data.status === 'healthy';
    } catch (error) {
      console.error('❌ 健康检查失败:', error);
      return false;
    }
  }

  /**
   * 更新API基础URL（用于网络切换）
   */
  updateBaseURL(newURL: string) {
    this.baseURL = newURL;
    console.log('🔄 试卷服务API地址已更新:', newURL);
  }
}

// 创建并导出单例
const paperService = new PaperService();
export default paperService;

