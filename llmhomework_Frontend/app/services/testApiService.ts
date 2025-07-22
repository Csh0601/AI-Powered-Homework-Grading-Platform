import apiService from './apiService';

export async function testUploadImage(dummyFile: { uri: string; name: string; type: string }) {
  try {
    const result = await apiService.uploadImage(dummyFile);
    console.log('上传图片接口测试通过:', result);
    return result;
  } catch (e) {
    console.error('上传图片接口测试失败:', e);
    return null;
  }
}

export async function testGenerateExercise() {
  try {
    const result = await apiService.generateExercise('测试知识点', false);
    console.log('题目生成接口测试通过:', result);
    return result;
  } catch (e) {
    console.error('题目生成接口测试失败:', e);
    return null;
  }
}

export async function testGetResults() {
  try {
    const result = await apiService.getResults();
    console.log('历史记录接口测试通过:', result);
    return result;
  } catch (e) {
    console.error('历史记录接口测试失败:', e);
    return null;
  }
}

export async function testBackendStatus() {
  try {
    const result = await apiService.checkBackendStatus();
    console.log('后端依赖状态接口测试通过:', result);
    return result;
  } catch (e) {
    console.error('后端依赖状态接口测试失败:', e);
    return null;
  }
} 