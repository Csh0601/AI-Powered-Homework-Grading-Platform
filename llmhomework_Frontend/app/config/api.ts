// API配置文件
export const API_CONFIG = {
    // 同一WiFi网络：使用电脑的WiFi IP地址
    BASE_URL: 'http://172.20.10.3:5000',  // 电脑在WiFi网络中的IP
    TIMEOUT: 120000, // 增加到2分钟，因为OCR处理需要时间
    RETRY_COUNT: 3,
  };

// 获取当前API地址
export const getApiUrl = () => {
  return API_CONFIG.BASE_URL;
};

// 开发环境常用IP地址参考
export const COMMON_DEV_IPS = [
  'http://localhost:5000',
  'http://192.168.1.100:5000',  // 请替换为您的实际IP
  'http://192.168.0.100:5000',
  'http://10.0.0.100:5000',
];
