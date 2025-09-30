import axios from 'axios';
import { Platform } from 'react-native';
import { API_CONFIG, checkMobileNetwork, getMobileRequestConfig } from '../config/api';
import { 
  GradingResponse, 
  GradingDataAdapter, 
  EnhancedGradingResponse,
  UploadRequest 
} from '../types/GradingTypes';

let BASE_URL = API_CONFIG.BASE_URL; // 使用let以便动态更新

const getCandidateUrls = () => {
  const urls = Array.isArray(API_CONFIG.CANDIDATE_URLS)
    ? API_CONFIG.CANDIDATE_URLS.slice()
    : [API_CONFIG.BASE_URL, API_CONFIG.FALLBACK_URL].filter(Boolean);

  if (Platform.OS === 'android') {
    if (!urls.includes('http://10.0.2.2:5000')) {
      urls.push('http://10.0.2.2:5000');
    }
  }

  const PRESET_URLS = [
    'http://172.29.15.82:5000',
    'http://172.19.168.76:5000',
    'http://172.28.131.217:5000',
    'http://172.24.96.93:5000',
    'http://192.168.137.1:5000',
  ];

  PRESET_URLS.forEach(url => {
    if (!urls.includes(url)) {
      urls.push(url);
    }
  });

  return urls;
};

const resolveBaseUrl = async () => {
  const candidates = getCandidateUrls();

  for (const url of candidates) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), API_CONFIG.CONNECTION_TIMEOUT);
      const response = await fetch(`${url}/status`, {
        method: 'GET',
        signal: controller.signal,
        headers: {
          'Connection': API_CONFIG.CONNECTION_TYPE,
          'Cache-Control': 'no-cache',
        },
      });
      clearTimeout(timeout);
      if (response.ok) {
        return url;
      }
    } catch (error) {
      // 忽略单个候选地址错误，尝试下一个
    }
  }

  return BASE_URL;
};

const apiService = {
  // 上传图片，返回批改结果和错题分析
  async uploadImage(image: { uri: string; name: string; type: string }, signal?: AbortSignal) {
    // 从文件名中提取任务ID（格式：taskId_image.jpg）
    const taskIdMatch = image.name.match(/^(task_[^_]+)/);
    const taskId = taskIdMatch ? taskIdMatch[1] : 'unknown_task';
    
    // 重试机制
    for (let attempt = 1; attempt <= API_CONFIG.RETRY_COUNT; attempt++) {
      try {
        console.log(`\n=== 📤 [${taskId}] API上传开始 (尝试 ${attempt}/${API_CONFIG.RETRY_COUNT}) ===`);
        
        return await this._performUpload(image, taskId, attempt, signal);
        
      } catch (error: any) {
        console.error(`❌ [${taskId}] 第${attempt}次尝试失败:`, error.message);
        
        // 详细分析错误类型
        let errorType = 'unknown';
        let errorMessage = error.message || 'Unknown error';
        
        if (error.message?.includes('Network Error')) {
          errorType = 'network';
        } else if (error.message?.includes('timeout') || error.code === 'ECONNABORTED') {
          errorType = 'timeout';
        } else if (error.message?.includes('connection abort') || error.message?.includes('aborted')) {
          errorType = 'connection_abort';
        } else if (error.code === 'ECONNREFUSED') {
          errorType = 'connection_refused';
        } else if (error.code === 'ENOTFOUND') {
          errorType = 'dns_error';
        } else if (error.response?.status === 400) {
          errorType = 'bad_request';
          // 检查是否是文件类型问题
          if (error.response?.data?.error?.includes('File type not allowed')) {
            errorType = 'file_type_error';
            errorMessage = '图片格式不支持，请确保上传 JPG、PNG 或 JPEG 格式的图片';
          } else if (error.response?.data?.error) {
            errorMessage = error.response.data.error;
          }
        } else if (error.response?.status >= 500) {
          errorType = 'server_error';
        }
        
        console.log(`🔍 [${taskId}] 错误类型: ${errorType}`);
        
        if (attempt === API_CONFIG.RETRY_COUNT) {
          // 最后一次尝试失败，抛出详细错误
          console.error(`💥 [${taskId}] 所有重试尝试均失败，错误类型: ${errorType}`);
          
          // 提供更友好的错误信息
          let userMessage = '上传失败';
          if (errorType === 'file_type_error') {
            userMessage = errorMessage; // 使用具体的文件类型错误信息
          } else if (errorType === 'timeout') {
            userMessage = 'AI批改需要较长时间，请检查网络连接后重试';
          } else if (errorType === 'network' || errorType === 'connection_abort') {
            userMessage = '网络连接中断，请检查网络状态后重试';
          } else if (errorType === 'connection_refused') {
            userMessage = '无法连接到服务器，请确认服务器状态';
          } else if (errorType === 'bad_request') {
            userMessage = errorMessage || '请求格式有误，请检查图片格式';
          } else if (errorType === 'server_error') {
            userMessage = '服务器暂时无法处理请求，请稍后重试';
          }
          
          throw new Error(`${userMessage} (${errorType})`);
        }
        
        // 对于文件类型错误，不进行重试
        if (errorType === 'file_type_error' || errorType === 'bad_request') {
          console.error(`💥 [${taskId}] 文件格式错误，停止重试: ${errorMessage}`);
          throw new Error(errorMessage);
        }
        
        // 根据错误类型和尝试次数调整等待时间（针对移动网络优化）
        let delay = 2000 * attempt; // 基础延迟增加
        if (errorType === 'connection_abort' || errorType === 'network') {
          // 移动网络连接中断，需要更长等待让网络恢复
          delay = Math.min(API_CONFIG.RETRY_DELAY * 2 * attempt, 10000); 
        } else if (errorType === 'timeout') {
          // 超时问题，适中等待 - 移动端减少等待时间
          delay = Math.min(API_CONFIG.RETRY_DELAY * 1.5 * attempt, 8000); 
        } else {
          // 其他错误，使用基础延迟
          delay = Math.min(API_CONFIG.RETRY_DELAY * attempt, 6000);
        }
        
        console.log(`⏳ [${taskId}] 等待 ${delay}ms 后进行第${attempt + 1}次尝试`);
        console.log(`🔧 [${taskId}] 错误分析: ${errorType} | 尝试: ${attempt}/${API_CONFIG.RETRY_COUNT}`);
        
        // 在重试前可以考虑进行快速网络检查
        if (errorType === 'network' && attempt < API_CONFIG.RETRY_COUNT) {
          console.log(`🔍 [${taskId}] 网络错误，等待期间进行网络状态检查...`);
          // 在等待期间被动检测网络是否恢复
          try {
            const probeBaseUrl = BASE_URL;
            const probeUrl = `${probeBaseUrl}/status?probe=${Date.now()}`;
            console.log(`🌐 [${taskId}] 网络探测: ${probeUrl}`);
            await axios.get(probeUrl, {
              timeout: API_CONFIG.CONNECTION_TIMEOUT,
            });
            console.log(`✅ [${taskId}] 网络探测成功，准备重试`);
          } catch (probeError: any) {
            console.log(`⚠️ [${taskId}] 网络探测失败: ${probeError?.message || probeError}`);
          }
        }
        
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  },

  // 实际执行上传的私有方法
  async _performUpload(image: { uri: string; name: string; type: string }, taskId: string, attempt: number, signal?: AbortSignal) {
    console.log(`📤 [${taskId}] 图片信息:`, {
      name: image.name,
      type: image.type,
      uri: image.uri.substring(0, 50) + '...'
    });
    console.log(`📤 [${taskId}] 图片URI类型:`, typeof image.uri);
    console.log(`📤 [${taskId}] 图片URI是否以data:开头:`, image.uri.startsWith('data:'));
    // 移动端智能网络预检查和地址选择（仅第1次尝试）
    let actualBaseUrl = BASE_URL;
    if (attempt === 1) {
      console.log(`📱 [${taskId}] 第1次尝试，进行移动端网络检查...`);
      try {
        const networkStatus = await checkMobileNetwork();
        if (networkStatus?.success && networkStatus.url) {
          console.log(`✅ [${taskId}] 移动端网络检查通过: ${networkStatus.url}`);
          actualBaseUrl = networkStatus.url;
          // 如果使用备用地址，记录切换
          if (networkStatus.url !== BASE_URL) {
            console.log(`🔄 [${taskId}] 切换到备用地址: ${networkStatus.url}`);
          }
        } else {
          console.warn(`⚠️ [${taskId}] 移动端网络检查失败，尝试备用地址...`);
          actualBaseUrl = API_CONFIG.FALLBACK_URL;
        }
      } catch (precheckError: any) {
        console.warn(`⚠️ [${taskId}] 网络预检查异常: ${precheckError.message}`);
        // 网络检查失败时使用原地址
        actualBaseUrl = BASE_URL;
      }
    }
    
    const formData = new FormData();

    // 检查是否是data URI
    if (image.uri.startsWith('data:')) {
      console.log(`🔄 [${taskId}] 检测到data URI，开始转换为Blob...`);
      try {
        // 将data URI转换为Blob对象
        const response = await fetch(image.uri);
        console.log(`✅ [${taskId}] fetch响应状态: ${response.status}`);
        const blob = await response.blob();
        console.log(`✅ [${taskId}] Blob对象创建成功 - 大小: ${blob.size}字节, 类型: ${blob.type}`);
        
        formData.append('file', blob, image.name);
        console.log(`✅ [${taskId}] FormData中添加了Blob对象，文件名: ${image.name}`);
      } catch (blobError: any) {
        console.error(`❌ [${taskId}] 转换Blob失败:`, blobError);
        throw new Error('转换图片数据失败: ' + blobError.message);
      }
    } else {
      console.log(`🔄 [${taskId}] 非data URI，使用文件路径方式...`);
      // 对于非data URI，使用React Native兼容的方式
      try {
        // React Native FormData需要特定的对象结构
        const fileObject = {
          uri: image.uri,
          name: image.name,
          type: image.type,
        };
        
        // 验证必要的属性
        if (!fileObject.uri || !fileObject.name || !fileObject.type) {
          throw new Error(`文件对象缺少必要属性: uri=${!!fileObject.uri}, name=${!!fileObject.name}, type=${!!fileObject.type}`);
        }
        
        formData.append('file', fileObject as any);
        console.log(`✅ [${taskId}] FormData中添加了文件对象:`, {
          uri: fileObject.uri.substring(0, 50) + '...',
          name: fileObject.name,
          type: fileObject.type
        });
      } catch (formDataError: any) {
        console.error(`❌ [${taskId}] FormData处理失败:`, formDataError.message);
        throw new Error(`文件上传准备失败: ${formDataError.message}`);
      }
    }
    
    // 检查FormData内容 (React Native兼容)
    console.log(`🔍 [${taskId}] FormData内容检查:`);
    try {
      // 在React Native中，FormData.entries()可能不可用，使用try-catch包装
      const formDataAny = formData as any;
      if (typeof formDataAny.entries === 'function') {
        for (let [key, value] of formDataAny.entries()) {
          console.log(`🔍 [${taskId}] - ${key}:`, value);
        }
      } else {
        console.log(`🔍 [${taskId}] FormData.entries()不可用，跳过内容检查`);
      }
    } catch (entriesError) {
      console.log(`🔍 [${taskId}] FormData内容检查跳过 (React Native环境)`);
    }
    
    console.log(`📡 [${taskId}] 发送POST请求到后端...`);
    
    // 使用移动端优化的请求配置 (React Native兼容)
    const mobileConfig = getMobileRequestConfig();
    const requestConfig = {
      ...mobileConfig,
      // React Native 专用配置
      responseType: 'json' as const,
      // 移除可能导致问题的配置项
      withCredentials: false,
      // 确保Content-Type由axios自动设置，避免boundary问题
      headers: {
        ...mobileConfig.headers,
        // 移除Content-Type，让axios自动设置multipart boundary
        'Content-Type': undefined,
      },
      // React Native网络层优化
      adapter: undefined,  // 使用默认adapter
      proxy: false,
      // 长时间请求支持
      timeout: mobileConfig.timeout,
      // 添加取消信号支持
      signal: signal,
    };
    
    console.log(`📡 [${taskId}] 请求配置:`, {
      url: `${actualBaseUrl}/upload_image`,
      timeout: requestConfig.timeout,
      headers: requestConfig.headers,
      selectedUrl: actualBaseUrl
    });
    
    const response = await axios.post(`${actualBaseUrl}/upload_image`, formData, requestConfig);
    
    console.log(`🎉 [${taskId}] 请求成功! 状态码: ${response.status}`);
    console.log(`📊 [${taskId}] 响应数据类型: ${typeof response.data}`);
    console.log(`📊 [${taskId}] 响应数据键: [${Object.keys(response.data || {}).join(', ')}]`);
    console.log(`📊 [${taskId}] 批改结果概览:`, {
      hasGradingResult: !!((response.data as any)?.grading_result),
      questionCount: (response.data as any)?.grading_result?.length || 0,
      hasWrongKnowledges: !!((response.data as any)?.wrong_knowledges),
      serverTaskId: (response.data as any)?.task_id || 'none'
    });
    console.log(`📄 [${taskId}] 完整响应数据:`, JSON.stringify(response.data, null, 2));
    
    // 处理和验证新格式的响应数据
    const processedData = this._processGradingResponse(response.data, taskId);
    
    return processedData;
  },

  // 处理批改响应数据（新格式适配）
  _processGradingResponse(rawData: any, taskId: string): GradingResponse {
    console.log(`🔄 [${taskId}] 开始处理批改响应数据...`);

    const normalizedRawData: any = rawData ? { ...rawData } : {};

    if (!normalizedRawData.summary || typeof normalizedRawData.summary !== 'object') {
      normalizedRawData.summary = {
        total_questions: 0,
        correct_count: 0,
        total_score: 0,
        accuracy_rate: 0,
        main_issues: [],
        knowledge_points: []
      };
    } else {
      const summary = { ...normalizedRawData.summary };
      const normalizeSummaryArray = (value: any) => {
        if (Array.isArray(value)) {
          return value.filter((item) => item !== null && item !== undefined);
        }
        if (value === null || value === undefined) {
          return [];
        }
        return [value];
      };

      summary.main_issues = normalizeSummaryArray(summary.main_issues);
      summary.knowledge_points = normalizeSummaryArray(summary.knowledge_points);

      normalizedRawData.summary = summary;
    }

    // 验证数据完整性
    const validationErrors = GradingDataAdapter.validateGradingResponse(normalizedRawData);
    if (validationErrors.length > 0) {
      console.warn(`⚠️ [${taskId}] 数据验证警告:`, validationErrors);
      
      // 如果是旧格式，尝试向前兼容
      if (!GradingDataAdapter.isNewFormat(normalizedRawData)) {
        console.log(`🔄 [${taskId}] 检测到旧格式数据，进行向前适配...`);
        return this._adaptOldFormatToNew(normalizedRawData, taskId);
      }
    }
    
    // 确保新格式数据的完整性
    const gradingData: GradingResponse = {
      questions: normalizedRawData.questions || [],
      grading_result: normalizedRawData.grading_result || [],
      summary: normalizedRawData.summary || {
        total_questions: 0,
        correct_count: 0,
        total_score: 0,
        accuracy_rate: 0,
        main_issues: [],
        knowledge_points: []
      },
      // 添加元数据
      ...normalizedRawData
    };
    
    // 数据增强处理
    this._enhanceGradingData(gradingData, taskId);
    
    console.log(`✅ [${taskId}] 批改数据处理完成`);
    console.log(`📊 [${taskId}] 处理结果: ${gradingData.summary.total_questions}道题, ${gradingData.summary.correct_count}题正确, 正确率${(gradingData.summary.accuracy_rate * 100).toFixed(1)}%`);
    
    return gradingData;
  },

  // 旧格式向新格式适配
  _adaptOldFormatToNew(oldData: any, taskId: string): GradingResponse {
    console.log(`🔄 [${taskId}] 执行旧格式到新格式的适配...`);
    
    // 构造新格式的数据结构
    const question = {
      number: "1",
      stem: oldData.question || "图片内容分析",
      answer: oldData.userAnswer || oldData.answer || "AI分析结果",
      type: oldData.type || "综合分析",
      question_id: oldData.questionId || `${taskId}_legacy_1`
    };
    
    const gradingResult = {
      question: question.stem,
      answer: question.answer,
      type: question.type,
      correct: oldData.isCorrect !== undefined ? oldData.isCorrect : false,
      score: oldData.score || 0,
      explanation: oldData.aiFeedback || oldData.explanation || "无详细说明",
      question_id: question.question_id,
      knowledge_points: oldData.knowledgePoint ? [oldData.knowledgePoint] : [],
      correct_answer: oldData.correct_answer
    };
    
    const summary = {
      total_questions: 1,
      correct_count: gradingResult.correct ? 1 : 0,
      total_score: gradingResult.score,
      accuracy_rate: gradingResult.correct ? 1.0 : 0.0,
      main_issues: oldData.main_issues || [],
      knowledge_points: gradingResult.knowledge_points
    };
    
    const adaptedData: GradingResponse = {
      questions: [question],
      grading_result: [gradingResult],
      summary: summary,
      // 保留原始字段以确保兼容性
      isCorrect: oldData.isCorrect,
      score: oldData.score,
      type: oldData.type,
      question: oldData.question,
      userAnswer: oldData.userAnswer,
      aiFeedback: oldData.aiFeedback,
      knowledgePoint: oldData.knowledgePoint,
      questionId: oldData.questionId
    };
    
    console.log(`✅ [${taskId}] 旧格式适配完成`);
    return adaptedData;
  },

  // 增强批改数据
  _enhanceGradingData(data: GradingResponse, taskId: string): void {
    console.log(`🔧 [${taskId}] 增强批改数据...`);
    
    // 添加任务ID和时间戳
    (data as any).taskId = taskId;
    (data as any).timestamp = new Date().toISOString();
    
    // 确保knowledge_points去重
    if (data.summary.knowledge_points) {
      data.summary.knowledge_points = [...new Set(data.summary.knowledge_points)];
    }
    
    // 为每个批改结果添加增强信息
    data.grading_result.forEach((result, index) => {
      // 确保knowledge_points是数组
      if (!Array.isArray(result.knowledge_points)) {
        result.knowledge_points = [];
      }
      
      // 确保learning_suggestions是数组
      if (result.learning_suggestions && !Array.isArray(result.learning_suggestions)) {
        result.learning_suggestions = [];
      }
      
      // 添加结果索引
      (result as any).resultIndex = index;
      
      // 如果没有explanation，提供默认说明
      if (!result.explanation || result.explanation.trim() === '') {
        result.explanation = result.correct ? 
          '答题正确，继续保持！' : 
          '答题有误，请仔细检查解题思路。';
      }
      
      // 保留新字段（learning_suggestions, similar_question）
      // 这些字段直接从原始数据传递，不做额外处理
    });
    
    // 确保main_issues是数组
    if (!Array.isArray(data.summary.main_issues)) {
      data.summary.main_issues = [];
    }
    
    // 确保summary中的新字段格式正确
    if (data.summary.learning_suggestions && !Array.isArray(data.summary.learning_suggestions)) {
      data.summary.learning_suggestions = [];
    }
    
    console.log(`✅ [${taskId}] 数据增强完成`);
  },

  // 健康检查 - 检查后端服务状态
  async healthCheck() {
    try {
      console.log('🩺 执行健康检查，目标URL:', `${BASE_URL}/`);
      const response = await axios.get(`${BASE_URL}/`, {
        timeout: 10000, // 10秒超时
      });
      console.log('✅ 健康检查成功:', response.data);
      return response.data;
    } catch (e: any) {
      console.error('❌ 健康检查失败:', e);
      throw new Error(e?.response?.data?.error || e?.message || '服务不可用');
    }
  },

  // 获取批改结果 - 通过task_id获取异步批改结果
  async getResult(taskId: string) {
    try {
      console.log('📄 获取批改结果，task_id:', taskId);
      const response = await axios.get(`${BASE_URL}/result/${taskId}`, {
        timeout: API_CONFIG.TIMEOUT,
      });
      console.log('✅ 获取结果成功:', response.data);
      return response.data;
    } catch (e: any) {
      console.error('❌ 获取结果失败:', e);
      throw new Error(e?.response?.data?.error || e?.message || '获取结果失败');
    }
  },

  // 获取AI服务状态 - 检查大模型服务可用性
  async getAIStatus() {
    try {
      console.log('🤖 检查AI服务状态，目标URL:', `${BASE_URL}/ai/status`);
      const response = await axios.get(`${BASE_URL}/ai/status`, {
        timeout: 10000,
      });
      console.log('✅ AI状态检查成功:', response.data);
      return response.data;
    } catch (e: any) {
      console.error('❌ AI状态检查失败:', e);
      throw new Error(e?.response?.data?.error || e?.message || 'AI服务检查失败');
    }
  },

  // 使用AI重新批改 - 支持指定使用AI模型批改
  async reGradeWithAI(taskId: string, useAI: boolean = true) {
    try {
      console.log('🤖 AI重新批改，task_id:', taskId, 'use_ai:', useAI);
      const response = await axios.post(`${BASE_URL}/regrade`, {
        task_id: taskId,
        use_ai: useAI,
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: API_CONFIG.TIMEOUT,
      });
      console.log('✅ AI重新批改成功:', response.data);
      return response.data;
    } catch (e: any) {
      console.error('❌ AI重新批改失败:', e);
      throw new Error(e?.response?.data?.error || e?.message || 'AI批改失败');
    }
  },

  // 获取知识点分析 - 基于题目内容进行知识点分析
  async getKnowledgeAnalysis(questionText: string) {
    try {
      console.log('🧠 获取知识点分析，题目文本长度:', questionText.length);
      const response = await axios.post(`${BASE_URL}/analyze/knowledge`, {
        question_text: questionText,
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: API_CONFIG.TIMEOUT,
      });
      console.log('✅ 知识点分析成功:', response.data);
      return response.data;
    } catch (e: any) {
      console.error('❌ 知识点分析失败:', e);
      throw new Error(e?.response?.data?.error || e?.message || '知识点分析失败');
    }
  },

  // 生成练习题 - 基于错题生成相似练习题
  async generatePractice(wrongQuestions: any[]) {
    try {
      console.log('📝 生成练习题，错题数量:', wrongQuestions.length);
      const response = await axios.post(`${BASE_URL}/generate/practice`, {
        wrong_questions: wrongQuestions,
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: API_CONFIG.TIMEOUT,
      });
      console.log('✅ 练习题生成成功:', response.data);
      return response.data;
    } catch (e: any) {
      console.error('❌ 练习题生成失败:', e);
      throw new Error(e?.response?.data?.error || e?.message || '练习题生成失败');
    }
  },

  // OCR单独识别 - 仅进行OCR识别，不批改
  async ocrOnly(image: { uri: string; name: string; type: string }) {
    try {
      console.log('👁️ OCR单独识别，图片信息:', image);
      const formData = new FormData();

      // 处理图片数据
      if (image.uri.startsWith('data:')) {
        const response = await fetch(image.uri);
        const blob = await response.blob();
        formData.append('file', blob, image.name);
      } else {
        formData.append('file', {
          uri: image.uri,
          name: image.name,
          type: image.type,
        } as any);
      }

      const response = await axios.post(`${BASE_URL}/ocr`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: API_CONFIG.TIMEOUT,
      });
      
      console.log('✅ OCR识别成功:', response.data);
      return response.data;
    } catch (e: any) {
      console.error('❌ OCR识别失败:', e);
      throw new Error(e?.response?.data?.error || e?.message || 'OCR识别失败');
    }
  },

  // 测试连接 - 测试与后端的网络连接
  async testConnection() {
    try {
      console.log('🔗 测试连接，目标服务器:', BASE_URL);
      const startTime = Date.now();
      const response = await axios.get(`${BASE_URL}/`, {
        timeout: 5000,
      });
      const endTime = Date.now();
      const latency = endTime - startTime;
      
      console.log(`✅ 连接测试成功，延迟: ${latency}ms`);
      return {
        success: true,
        latency,
        server: BASE_URL,
        status: response.data,
      };
    } catch (e: any) {
      console.error('❌ 连接测试失败:', e);
      return {
        success: false,
        error: e?.message || '连接失败',
        server: BASE_URL,
      };
    }
  },
};

export default apiService;