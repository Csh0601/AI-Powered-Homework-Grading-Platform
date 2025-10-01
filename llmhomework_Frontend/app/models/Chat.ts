/**
 * 对话相关的数据模型
 */

/**
 * 消息角色类型
 */
export type MessageRole = 'user' | 'assistant' | 'system';

/**
 * 单条消息
 */
export interface ChatMessage {
  role: MessageRole;
  content: string;
  timestamp: string;
}

/**
 * 对话会话
 */
export interface Conversation {
  conversationId: string;
  taskId: string;
  messages: ChatMessage[];
  createdAt: string;
  lastActivity?: string;
}

/**
 * 开始对话的请求
 */
export interface StartConversationRequest {
  task_id: string;
  grading_result: any;  // 批改结果对象
}

/**
 * 开始对话的响应
 */
export interface StartConversationResponse {
  success: boolean;
  conversation_id: string;
  welcome_message: string;
  message: string;
  error?: string;
}

/**
 * 发送消息的请求
 */
export interface SendMessageRequest {
  conversation_id: string;
  message: string;
}

/**
 * 发送消息的响应
 */
export interface SendMessageResponse {
  success: boolean;
  response: string;
  conversation_id: string;
  message_count: number;
  error?: string;
}

/**
 * 获取历史的响应
 */
export interface GetHistoryResponse {
  success: boolean;
  messages: ChatMessage[];
  message_count: number;
  error?: string;
}
