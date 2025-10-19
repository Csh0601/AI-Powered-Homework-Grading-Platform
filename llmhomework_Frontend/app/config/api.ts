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

// 🔄 动态IP配置 - 自动适配校园网环境
// 系统会自动尝试所有校园网段的IP，无需手动修改
const NETWORK_PRESETS = [
  // 当前会话检测到的IP会自动添加到最前面
  // 以下是常见的校园网IP段，系统会自动遍历尝试
  'http://172.28.140.34:5000',     // 历史IP (2025-10-10)
  'http://172.29.15.82:5000',      // 校园网段A
  'http://172.19.168.76:5000',     // 校园网段B
  'http://172.28.131.217:5000',    // 校园网段C
  'http://172.24.96.93:5000',      // 校园网段D
  'http://192.168.137.1:5000',     // 本地热点
  'http://192.168.1.1:5000',       // 常见路由器网段
  'http://192.168.0.1:5000',       // 常见路由器网段
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
    // 🔄 主要后端服务器地址（自动尝试可用IP）
    // 系统会自动探测并连接到可用的服务器
    BASE_URL: CANDIDATE_URLS[0],
    
    // 备用服务器地址（如果主地址失败）
    FALLBACK_URL: CANDIDATE_URLS[1] || CANDIDATE_URLS[0],

    // 候选地址列表（网络探测会自动遍历）
    // 包含自动检测的IP和预设的校园网IP段
    CANDIDATE_URLS,
    
    // 🌐 自动IP探测配置
    AUTO_DETECT_IP: true,         // 启用自动IP检测
    DETECT_TIMEOUT: 3000,         // 单个IP检测超时：3秒
    PARALLEL_DETECT: true,        // 启用并行检测（加快速度）
    
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

// 🌐 开发环境IP地址配置说明（自动适配）
export const NETWORK_CONFIG = {
  // 🎯 本地开发配置
  LOCALHOST: 'http://127.0.0.1:5000',        // 本地开发，Web端测试
  
  // 🏫 校园网配置（系统会自动检测并连接）
  // 深圳大学校园网段：172.16.0.0 - 172.31.255.255
  CAMPUS_NETWORK_RANGE: '172.16.0.0/12',     // 校园网IP段
  
  // 📱 常见网络配置
  WIFI_COMMON: '192.168.x.x',                // 常见WiFi网段
  HOTSPOT: 'http://192.168.137.1:5000',      // 本地热点IP
  
  // ✅ 自动化配置说明
  // 1. 系统会自动检测可用的后端服务器IP
  // 2. 无需手动修改IP地址，支持任何校园网环境
  // 3. 自动尝试所有候选IP，优先连接最快的服务器
  // 4. 如果自动检测失败，请检查：
  //    - 后端服务是否已启动（运行 start_backends.bat）
  //    - 防火墙是否允许端口5000访问
  //    - 电脑和手机是否在同一网络（校园网/同一WiFi）
  // 5. 查看当前IP：Windows运行 ipconfig，Mac/Linux运行 ifconfig
  
  // 🔧 手动指定IP（仅在自动检测失败时使用）
  MANUAL_IP: null,  // 设置为 'http://你的IP:5000' 来手动指定
};

// 备选IP地址列表（按优先级排序）
export const COMMON_DEV_IPS = [
  'http://127.0.0.1:5000',        // 最稳定：本地开发
  'http://172.29.15.82:5000',     // 以太网：校园网环境
  'http://172.24.96.93:5000',     // WiFi：无线网络环境
  'http://192.168.137.1:5000',    // 热点：移动热点共享
  'http://localhost:5000',        // 同127.0.0.1，某些环境下可能不同
];
