import apiService from './apiService';

// ✅ 此测试函数仍然有效
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

/*
 * ⚠️ 以下测试函数已过时 - 相关API端点不再存在
 *
 * 如需重新启用，请先确认后端API已实现相应的端点：
 * - generateExercise: 题目生成接口
 * - getResults: 历史记录接口
 * - checkBackendStatus: 后端依赖状态检查接口
 */

/*
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
*/ 