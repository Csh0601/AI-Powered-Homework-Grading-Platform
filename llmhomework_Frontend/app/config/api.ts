import Constants from 'expo-constants';
import { Platform } from 'react-native';

// API配置文件 - 移动端网络优化版本

const BACKEND_PORT = 5000;

const normalizeUrl = (input?: string | null, port: number = BACKEND_PORT) => {
  if (!input) return null;
  let urlCandidate = input.trim();
  if (!urlCandidate) return null;

  // 如果提供的是host:port或host，补全协议
  if (!/^https?:\/\//i.test(urlCandidate)) {
    urlCandidate = `http://${urlCandidate}`;
  }

  try {
    const parsed = new URL(urlCandidate);
    const hostname = parsed.hostname;
    const protocol = parsed.protocol || 'http:';
    const finalPort = parsed.port ? parsed.port : port.toString();
    if (!hostname) return null;
    return `${protocol}//${hostname}:${finalPort}`;
  } catch (error) {
    return null;
  }
};

const extractHostFromUri = (uri?: string | null) => {
  if (!uri) return null;
  const trimmed = uri.trim();
  if (!trimmed) return null;

  // 某些场景（如 exp://192.168.1.100:8081 ）需要兼容处理
  try {
    const parsed = new URL(trimmed.includes('://') ? trimmed : `http://${trimmed}`);
    return parsed.hostname || null;
  } catch (error) {
    const withoutQuery = trimmed.split('?')[0];
    const host = withoutQuery.replace(/^.*\b(\d{1,3}(?:\.\d{1,3}){3})\b.*$/, '$1');
    return host && host !== withoutQuery ? host : null;
  }
};

const detectDevServerHost = () => {
  const expoConfig = Constants.expoConfig as any;
  const manifest = (Constants as any).manifest as any;
  const manifest2 = (Constants as any).manifest2 as any;

  const candidateUris = [
    expoConfig?.hostUri,
    expoConfig?.extra?.expoClient?.hostUri,
    expoConfig?.extra?.backendHost,
    expoConfig?.extra?.apiHost,
    expoConfig?.extra?.apiUrl,
    manifest?.debuggerHost,
    manifest?.hostUri,
    manifest?.bundleUrl,
    manifest2?.extra?.expoClient?.hostUri,
    Constants.linkingUri,
    process.env?.EXPO_PUBLIC_API_URL,
    process.env?.API_BASE_URL,
  ];

  for (const uri of candidateUris) {
    const host = extractHostFromUri(uri);
    if (host && host !== '127.0.0.1' && host !== 'localhost') {
      return host;
    }
  }

  return null;
};

const detectedHost = detectDevServerHost();

const CANDIDATE_URLS = Array.from(
  new Set(
    [
      normalizeUrl(detectedHost ? `${detectedHost}:${BACKEND_PORT}` : null),
      normalizeUrl(Constants.expoConfig?.extra?.apiUrl),
      normalizeUrl(Constants.expoConfig?.extra?.backendUrl),
      normalizeUrl(process.env?.EXPO_PUBLIC_API_URL),
      normalizeUrl(process.env?.API_BASE_URL),
      Platform.select({ android: normalizeUrl('10.0.2.2'), default: null }),
      normalizeUrl('127.0.0.1'),
      normalizeUrl('localhost'),
    ].filter(Boolean) as string[]
  )
);

const NETWORK_PRESETS = [
  'http://172.29.15.82:5000',
  'http://172.19.168.76:5000',
  'http://172.28.131.217:5000',
  'http://172.24.96.93:5000',
  'http://192.168.137.1:5000',
];

NETWORK_PRESETS.forEach(url => {
  if (!CANDIDATE_URLS.includes(url)) {
    CANDIDATE_URLS.push(url);
  }
});

// 至少保证有一个默认值
if (CANDIDATE_URLS.length === 0) {
  CANDIDATE_URLS.push('http://127.0.0.1:5000');
}

export const API_CONFIG = {
    // 主要后端服务器地址（自动尝试可用IP）
    BASE_URL: CANDIDATE_URLS[0],
    
    // 备用服务器地址（如果主地址失败）
    FALLBACK_URL: CANDIDATE_URLS[1] || CANDIDATE_URLS[0],

    // 候选地址列表（网络探测会自动遍历）
    CANDIDATE_URLS,
    
    // 移动端网络优化配置
    TIMEOUT: 300000,              // 移动端专用超时：5分钟
    CONNECTION_TIMEOUT: 15000,    // 连接超时：15秒
    RETRY_COUNT: 3,               // 重试次数
    RETRY_DELAY: 5000,            // 重试延迟：5秒
    
    // 移动端网络优化
    USE_KEEP_ALIVE: false,        // 禁用Keep-Alive
    CONNECTION_TYPE: 'close',     // 连接类型
    
    // 上传配置
    UPLOAD_CHUNK_SIZE: 1024 * 1024, // 1MB分块
    
    // 调试配置
    ENABLE_NETWORK_LOGS: true,
    LOG_REQUEST_DETAILS: true,
    LOG_RESPONSE_HEADERS: true,
  } as const;

// 获取API地址（带备用机制）
export const getApiUrl = (useFallback = false) => {
    return useFallback ? API_CONFIG.FALLBACK_URL : API_CONFIG.BASE_URL;
};

// 移动端网络检查
export const checkMobileNetwork = async () => {
    console.log('📱 [Mobile] 检查网络连接...');
    
    try {
        // 首先尝试主地址
        const response = await fetch(API_CONFIG.BASE_URL + '/status', {
            method: 'GET',
            headers: {
                'Connection': API_CONFIG.CONNECTION_TYPE,
                'Cache-Control': 'no-cache'
            }
        });
        
        if (response.ok) {
            console.log('✅ [Mobile] 主地址连接正常');
            return { success: true, url: API_CONFIG.BASE_URL };
        }
    } catch (error) {
        console.log('⚠️ [Mobile] 主地址连接失败，尝试备用地址...');
    }
    
    try {
        // 尝试备用地址
        const fallbackResponse = await fetch(API_CONFIG.FALLBACK_URL + '/status', {
            method: 'GET',
            headers: {
                'Connection': API_CONFIG.CONNECTION_TYPE,
                'Cache-Control': 'no-cache'
            }
        });
        
        if (fallbackResponse.ok) {
            console.log('✅ [Mobile] 备用地址连接正常');
            return { success: true, url: API_CONFIG.FALLBACK_URL };
        }
    } catch (fallbackError) {
        console.log('❌ [Mobile] 所有地址连接失败');
        return { success: false, error: 'All endpoints failed' };
    }
};

// 移动端专用请求配置
export const getMobileRequestConfig = (useFallback = false) => {
    return {
        timeout: API_CONFIG.TIMEOUT,
        headers: {
            // 注意：不设置Content-Type，让axios自动处理multipart boundary
            'Accept': 'application/json',
            'Connection': API_CONFIG.CONNECTION_TYPE,
            'Cache-Control': 'no-cache',
            'User-Agent': 'LLMHomeworkMobile/1.0',
        },
        maxContentLength: Infinity,
        maxBodyLength: Infinity,
        validateStatus: (status: number) => status >= 200 && status < 300,
        maxRedirects: 0,
        // React Native 专用配置
        transitional: {
            silentJSONParsing: false,
            forcedJSONParsing: true,
            clarifyTimeoutError: true
        }
    };
};

// 开发环境IP地址配置说明
export const NETWORK_CONFIG = {
  // 🎯 当前推荐配置（最稳定）
  LOCALHOST: 'http://127.0.0.1:5000',        // 本地开发，Web端测试
  
  // 🏫 校园网配置（深圳大学 campus.szu.edu.cn）
  CAMPUS_A: 'http://172.29.15.82:5000',      // 校区A网络段
  CAMPUS_B: 'http://172.19.168.76:5000',     // 校区B网络段
  CAMPUS_CURRENT: 'http://172.28.131.217:5000', // 当前网络段（2025-09-24）
  
  // 📱 其他网络配置
  WIFI_OLD: 'http://172.24.96.93:5000',      // WiFi IP（无线网络-旧）
  HOTSPOT: 'http://192.168.137.1:5000',      // 本地热点IP
  
  // ⚠️ 网络问题解决方案
  // 1. 如果出现 "Network Error"，首先检查后端是否启动
  // 2. 使用 ipconfig 查看当前IP地址
  // 3. 确保防火墙允许端口5000访问
  // 4. 校区切换时需要更新 API_CONFIG.BASE_URL
  // 5. 运行 node check_network.js 检查当前网络配置
  // 4. 手机测试时，确保与电脑在同一WiFi网络
};

// 备选IP地址列表（按优先级排序）
export const COMMON_DEV_IPS = [
  'http://127.0.0.1:5000',        // 最稳定：本地开发
  'http://172.29.15.82:5000',     // 以太网：校园网环境
  'http://172.24.96.93:5000',     // WiFi：无线网络环境
  'http://192.168.137.1:5000',    // 热点：移动热点共享
  'http://localhost:5000',        // 同127.0.0.1，某些环境下可能不同
];
