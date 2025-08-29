import axios from 'axios';
import { API_CONFIG } from '../config/api';

const BASE_URL = API_CONFIG.BASE_URL;

const apiService = {
  // 上传图片，返回批改结果和错题分析
  async uploadImage(image: { uri: string; name: string; type: string }) {
    try {
      console.log('API请求开始，目标URL:', `${BASE_URL}/upload_image`);
      const formData = new FormData();
      formData.append('file', {
        uri: image.uri,
        name: image.name,
        type: image.type,
      } as any);
      
      console.log('发送POST请求...');
      const response = await axios.post(`${BASE_URL}/upload_image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: API_CONFIG.TIMEOUT,
      });
      
      console.log('✅ 请求成功，状态码:', response.status);
      console.log('✅ 响应数据类型:', typeof response.data);
      console.log('✅ 响应数据键:', Object.keys(response.data || {}));
      console.log('✅ 完整响应数据:', JSON.stringify(response.data, null, 2));
      
      return response.data;
    } catch (e: any) {
      console.error('API请求失败详情:', e);
      if (e.response) {
        console.error('错误响应状态:', e.response.status);
        console.error('错误响应数据:', e.response.data);
      } else if (e.request) {
        console.error('请求发送失败:', e.request);
      } else {
        console.error('请求配置错误:', e.message);
      }
      throw new Error(e?.response?.data?.error || e?.message || '上传图片失败');
    }
  },

  // 获取历史批改结果
  async getResults(userId?: string, taskId?: string) {
    try {
      const params: any = {};
      if (userId) params.user_id = userId;
      if (taskId) params.task_id = taskId;
      const response = await axios.get(`${BASE_URL}/get_results`, { params });
      return response.data;
    } catch (e: any) {
      throw new Error(e?.response?.data?.error || e?.message || '获取历史记录失败');
    }
  },

  // 题目生成（支持use_gpt参数）
  async generateExercise(knowledge: string, use_gpt = false) {
    try {
      const response = await axios.post(`${BASE_URL}/generate_exercise`, { knowledge, use_gpt });
      return response.data;
    } catch (e: any) {
      throw new Error(e?.response?.data?.error || e?.message || '题目生成失败');
    }
  },

  // 检查后端依赖状态
  async checkBackendStatus() {
    try {
      const response = await axios.get(`${BASE_URL}/status`);
      return response.data;
    } catch (e) {
      return { status: 'unreachable', error: e };
    }
  },
};

export default apiService;
