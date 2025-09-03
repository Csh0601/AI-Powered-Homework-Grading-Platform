// API配置文件
export const API_CONFIG = {
    // 同一WiFi网络：使用电脑的WiFi IP地址
    BASE_URL: 'http://172.28.138.140:5000',  // 更改为实际后端服务器IP地址
    TIMEOUT: 120000, // 增加到2分钟，因为OCR处理需要时间
    RETRY_COUNT: 3,
  };

// 获取当前API地址
export const getApiUrl = () => {
  return API_CONFIG.BASE_URL;
};

// 开发环境常用IP地址参考
export const COMMON_DEV_IPS = [
  'http://172.28.138.140:5000', // 当前使用：实际后端服务器IP地址
  'http://localhost:5000',      // 仅适用于电脑本地调试，手机无法访问
  'http://127.0.0.1:5000',      // 备选：与localhost相同，手机无法访问
  'http://172.29.15.89:5000',   // 历史网络IP（宿舍楼）
  'http://172.20.10.3:5000',    // 历史网络IP（学院楼）
];
