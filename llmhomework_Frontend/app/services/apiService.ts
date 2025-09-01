import axios from 'axios';
import { API_CONFIG } from '../config/api';

const BASE_URL = API_CONFIG.BASE_URL;

const apiService = {
  // 上传图片，返回批改结果和错题分析
  async uploadImage(image: { uri: string; name: string; type: string }) {
    try {
      console.log('=== 开始上传图片 ===');
      console.log('图片信息:', image);
      console.log('图片URI类型:', typeof image.uri);
      console.log('图片URI是否以data:开头:', image.uri.startsWith('data:'));
      console.log('API请求开始，目标URL:', `${BASE_URL}/upload_image`);
      
      const formData = new FormData();

      // 检查是否是data URI
      if (image.uri.startsWith('data:')) {
        console.log('检测到data URI，开始转换...');
        try {
          // 将data URI转换为Blob对象
          const response = await fetch(image.uri);
          console.log('fetch响应状态:', response.status);
          const blob = await response.blob();
          console.log('Blob对象创建成功:', blob);
          console.log('Blob大小:', blob.size, '字节');
          console.log('Blob类型:', blob.type);
          
          formData.append('file', blob, image.name);
          console.log('✅ FormData中添加了Blob对象，文件名:', image.name);
        } catch (blobError: any) {
          console.error('转换Blob失败:', blobError);
          throw new Error('转换图片数据失败: ' + blobError.message);
        }
      } else {
        console.log('非data URI，使用原有方式...');
        // 对于非data URI（例如本地文件路径），保持原有的处理方式
        formData.append('file', {
          uri: image.uri,
          name: image.name,
          type: image.type,
        } as any);
        console.log('✅ FormData中添加了文件对象');
      }
      
      // 检查FormData内容
      console.log('FormData内容检查:');
      // @ts-ignore - FormData.entries() 在大多数现代浏览器中可用
      for (let [key, value] of formData.entries()) {
        console.log(`- ${key}:`, value);
      }
      
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
      console.error('❌ API请求失败详情:', e);
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
  // ... other functions ...
};

export default apiService;