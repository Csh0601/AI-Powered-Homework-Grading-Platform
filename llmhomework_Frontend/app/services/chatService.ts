/**
 * 对话服务
 * 处理与后端对话API的交互
 */

import { API_CONFIG } from '../config/api';
import type {
  StartConversationRequest,
  StartConversationResponse,
  SendMessageRequest,
  SendMessageResponse,
  GetHistoryResponse,
  ChatMessage
} from '../models/Chat';

/**
 * 对话服务类
 */
class ChatService {
  private baseUrl: string;
  private timeout: number;

  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
    this.timeout = API_CONFIG.TIMEOUT;
  }

  /**
   * 带超时的fetch请求（兼容React Native）
   * 使用 AbortController + setTimeout 替代 AbortSignal.timeout
   */
  private async fetchWithTimeout(
    url: string,
    options: RequestInit,
    timeoutMs: number
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      controller.abort();
    }, timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error: any) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new Error('请求超时，请检查网络连接');
      }
      throw error;
    }
  }

  /**
   * 开始新对话
   * @param taskId 批改任务ID
   * @param gradingResult 批改结果数据
   * @returns 对话会话信息
   */
  async startConversation(
    taskId: string,
    gradingResult: any
  ): Promise<StartConversationResponse> {
    console.log('🚀 [ChatService] 开始创建对话:', taskId);

    try {
      const requestData: StartConversationRequest = {
        task_id: taskId,
        grading_result: gradingResult
      };

      const response = await this.fetchWithTimeout(
        `${this.baseUrl}/api/chat/start`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify(requestData),
        },
        this.timeout
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const result: StartConversationResponse = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || '创建对话失败');
      }

      console.log('✅ [ChatService] 对话创建成功:', result.conversation_id);
      return result;

    } catch (error: any) {
      console.error('❌ [ChatService] 创建对话失败:', error);
      
      if (error.name === 'AbortError' || error.name === 'TimeoutError') {
        throw new Error('网络请求超时，请检查网络连接');
      }
      
      throw new Error(error.message || '创建对话失败');
    }
  }

  /**
   * 发送消息
   * @param conversationId 对话会话ID
   * @param message 用户消息内容
   * @returns AI回复结果
   */
  async sendMessage(
    conversationId: string,
    message: string
  ): Promise<SendMessageResponse> {
    console.log('💬 [ChatService] 发送消息:', conversationId);

    try {
      const requestData: SendMessageRequest = {
        conversation_id: conversationId,
        message: message.trim()
      };

      const response = await this.fetchWithTimeout(
        `${this.baseUrl}/api/chat/message`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify(requestData),
        },
        this.timeout
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const result: SendMessageResponse = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || '发送消息失败');
      }

      console.log('✅ [ChatService] 消息发送成功');
      return result;

    } catch (error: any) {
      console.error('❌ [ChatService] 发送消息失败:', error);
      
      if (error.name === 'AbortError' || error.name === 'TimeoutError') {
        throw new Error('网络请求超时，AI可能正在思考，请稍后重试');
      }
      
      throw new Error(error.message || '发送消息失败');
    }
  }

  /**
   * 获取对话历史
   * @param conversationId 对话会话ID
   * @returns 对话历史消息列表
   */
  async getHistory(conversationId: string): Promise<GetHistoryResponse> {
    console.log('📜 [ChatService] 获取对话历史:', conversationId);

    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}/api/chat/history/${encodeURIComponent(conversationId)}`,
        {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
        },
        this.timeout
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const result: GetHistoryResponse = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || '获取历史失败');
      }

      console.log(`✅ [ChatService] 获取历史成功，消息数: ${result.message_count}`);
      return result;

    } catch (error: any) {
      console.error('❌ [ChatService] 获取历史失败:', error);
      
      if (error.name === 'AbortError' || error.name === 'TimeoutError') {
        throw new Error('网络请求超时');
      }
      
      throw new Error(error.message || '获取对话历史失败');
    }
  }

  /**
   * 检查对话服务健康状态
   * @returns 健康状态信息
   */
  async checkHealth(): Promise<any> {
    console.log('🏥 [ChatService] 检查服务健康状态');

    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}/api/chat/health`,
        {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
        },
        10000 // 健康检查10秒超时
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();
      console.log('✅ [ChatService] 服务健康状态:', result);
      return result;

    } catch (error: any) {
      console.error('❌ [ChatService] 健康检查失败:', error);
      throw error;
    }
  }

  /**
   * 更新API基础URL
   * @param newBaseUrl 新的基础URL
   */
  updateBaseUrl(newBaseUrl: string): void {
    this.baseUrl = newBaseUrl;
    console.log('🔄 [ChatService] API地址已更新:', newBaseUrl);
  }
}

// 导出单例实例
export const chatService = new ChatService();

// 导出类供测试使用
export default ChatService;
