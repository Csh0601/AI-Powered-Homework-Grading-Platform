# 📱 手机APP打包完整指南

## 一、前置准备

### 1. 安装 EAS CLI (Expo Application Services)
```bash
npm install -g eas-cli
```

### 2. 登录/注册 Expo 账号
```bash
eas login
```
如果没有账号,访问 https://expo.dev/ 注册一个免费账号

### 3. 配置项目
```bash
cd llmhomework_Frontend
eas build:configure
```

---

## 二、打包 Android APK (推荐方式)

### 方法一:使用 EAS Build (云端打包,推荐)

#### 步骤1:构建APK
```bash
cd llmhomework_Frontend
eas build --platform android --profile preview
```

**说明:**
- `preview` 配置会生成 APK 文件(可直接安装)
- `production` 配置会生成 AAB 文件(用于上架Google Play)
- 首次构建需要10-30分钟
- 构建完成后会提供下载链接

#### 步骤2:下载APK
构建完成后:
1. 在命令行中点击提供的链接
2. 或访问 https://expo.dev/accounts/你的用户名/projects/llmhomework/builds
3. 下载生成的 `.apk` 文件

#### 步骤3:安装到手机
- 将APK传到手机
- 打开文件管理器,点击APK安装
- 可能需要允许"未知来源"的应用安装权限

---

### 方法二:本地打包 (需要Android Studio)

#### 前置要求:
1. 安装 Android Studio
2. 配置 Android SDK
3. 配置 Java JDK

#### 打包命令:
```bash
cd llmhomework_Frontend

# 1. 导出Android项目
npx expo prebuild --platform android

# 2. 构建APK
cd android
./gradlew assembleRelease  # Windows使用: gradlew.bat assembleRelease

# 3. 找到生成的APK
# 位置: android/app/build/outputs/apk/release/app-release.apk
```

---

## 三、打包 iOS APP (需要Mac和Apple开发者账号)

### 使用 EAS Build
```bash
cd llmhomework_Frontend
eas build --platform ios --profile production
```

**注意:**
- iOS打包必须有Apple开发者账号($99/年)
- 需要配置证书和描述文件
- 可以生成 `.ipa` 文件通过TestFlight分发

---

## 四、一键打包脚本

### Android APK 一键打包
创建 `build_android.bat`:
```bash
@echo off
echo ================================
echo   AI学习伙伴 Android APK打包
echo ================================
echo.

cd llmhomework_Frontend

echo [步骤1] 检查EAS CLI...
call eas whoami
if errorlevel 1 (
    echo 请先登录: eas login
    pause
    exit /b 1
)

echo.
echo [步骤2] 开始构建Android APK...
echo 这可能需要10-30分钟,请耐心等待...
call eas build --platform android --profile preview

echo.
echo ================================
echo   构建完成!
echo   请访问上方链接下载APK文件
echo ================================
pause
```

### 同时打包 Android + iOS
创建 `build_all.bat`:
```bash
@echo off
cd llmhomework_Frontend
eas build --platform all --profile production
```

---

## 五、更新APP版本

每次更新APP时:

### 1. 修改版本号
编辑 `app.json`:
```json
{
  "expo": {
    "version": "1.0.1",  // 更新这里
    "android": {
      "versionCode": 2    // Android版本号+1
    },
    "ios": {
      "buildNumber": "1.0.1"  // iOS版本号
    }
  }
}
```

### 2. 重新构建
```bash
eas build --platform android --profile preview
```

---

## 六、常见问题解决

### 问题1: 后端服务器连接
APP需要连接到后端服务器,确保修改API配置:

**修改 `llmhomework_Frontend/app/config/api.ts`:**
```typescript
// 本地测试
export const API_BASE_URL = 'http://你的电脑IP:5000';

// 生产环境(需要部署后端到云服务器)
export const API_BASE_URL = 'https://你的域名.com';
```

### 问题2: 网络权限
确保 `app.json` 中配置了网络权限:
```json
"android": {
  "permissions": [
    "INTERNET",
    "CAMERA",
    "READ_EXTERNAL_STORAGE",
    "WRITE_EXTERNAL_STORAGE"
  ]
}
```

### 问题3: 图片选择器不工作
需要添加相机和存储权限,已在配置中包含。

### 问题4: 构建失败
- 检查 `package.json` 依赖是否正确
- 运行 `npm install` 确保依赖安装完整
- 查看 EAS 构建日志获取详细错误信息

---

## 七、发布到应用商店

### Google Play (Android)
1. 注册 Google Play 开发者账号 ($25一次性费用)
2. 使用 `production` 配置构建 AAB:
   ```bash
   eas build --platform android --profile production
   ```
3. 上传到 Google Play Console
4. 填写应用信息、截图、描述
5. 提交审核(通常1-3天)

### Apple App Store (iOS)
1. 注册 Apple 开发者账号 ($99/年)
2. 构建iOS应用:
   ```bash
   eas build --platform ios --profile production
   ```
3. 使用 EAS Submit 提交:
   ```bash
   eas submit --platform ios
   ```
4. 在 App Store Connect 完善信息
5. 提交审核(通常1-7天)

---

## 八、后端部署建议

手机APP需要后端支持,建议将Flask后端部署到云服务器:

### 推荐平台:
1. **阿里云ECS** - 适合国内用户
2. **腾讯云** - 性价比高
3. **AWS / Azure** - 国际化选择
4. **Heroku** - 免费试用(有限制)

### 部署后:
1. 获取服务器公网IP或域名
2. 修改前端API配置指向服务器
3. 重新打包APP

---

## 九、快速开始(推荐流程)

```bash
# 1. 安装EAS CLI
npm install -g eas-cli

# 2. 登录Expo
eas login

# 3. 配置项目
cd llmhomework_Frontend
eas build:configure

# 4. 构建Android APK
eas build --platform android --profile preview

# 5. 等待构建完成,下载APK

# 6. 安装到手机测试
```

---

## 十、文件说明

- `app.json` - Expo应用配置,包含应用名称、图标、权限等
- `eas.json` - EAS Build配置,定义不同的构建配置
- `package.json` - 依赖管理

---

## 技术支持

如遇到问题:
1. 查看 Expo 文档: https://docs.expo.dev/
2. 查看 EAS Build 文档: https://docs.expo.dev/build/introduction/
3. Expo 社区论坛: https://forums.expo.dev/

**祝你打包顺利! 🎉**























