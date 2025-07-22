import axios from 'axios';

const BASE_URL = 'http://192.168.2.131:5000'; // 按实际后端IP填写

const apiService = {
  // 上传图片，返回批改结果和错题分析
  async uploadImage(image: { uri: string; name: string; type: string }) {
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: image.uri,
        name: image.name,
        type: image.type,
      } as any);
      const response = await axios.post(`${BASE_URL}/upload_image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (e: any) {
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
