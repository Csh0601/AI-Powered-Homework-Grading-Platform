// 连接验证脚本
const axios = require('axios');

const BACKEND_URL = 'http://172.28.138.140:5000';

async function verifyConnection() {
  console.log('🔍 正在验证后端连接...');
  console.log(`目标地址: ${BACKEND_URL}`);
  
  try {
    console.log('\n1️⃣ 测试基本连接...');
    const response = await axios.get(`${BACKEND_URL}/status`, {
      timeout: 10000
    });
    console.log('✅ 基本连接成功!');
    console.log('响应状态:', response.status);
    console.log('响应数据:', response.data);
    
    console.log('\n2️⃣ 测试健康检查...');
    try {
      const healthResponse = await axios.get(`${BACKEND_URL}/`, {
        timeout: 5000
      });
      console.log('✅ 健康检查成功!');
      console.log('健康检查响应:', healthResponse.data);
    } catch (healthError) {
      console.log('⚠️ 健康检查失败，但基本连接正常');
    }
    
    console.log('\n🎉 连接验证完成！前端配置正确，可以访问后端服务。');
    
  } catch (error) {
    console.error('\n❌ 连接失败!');
    console.error('错误类型:', error.code || 'UNKNOWN');
    console.error('错误信息:', error.message);
    
    if (error.code === 'ECONNREFUSED') {
      console.log('\n💡 可能的解决方案:');
      console.log('1. 确保后端服务正在运行');
      console.log('2. 检查IP地址是否正确: 172.28.138.140');
      console.log('3. 确保防火墙允许5000端口');
      console.log('4. 确保手机和电脑在同一网络');
    } else if (error.code === 'ENOTFOUND') {
      console.log('\n💡 可能的解决方案:');
      console.log('1. 检查网络连接');
      console.log('2. 确认IP地址正确');
      console.log('3. 确保手机和电脑在同一WiFi网络');
    }
  }
}

verifyConnection();
