// 🎨 智学伴 - Apple 冷色调设计系统
// 核心理念：让智学伴育莘莘学子
// 设计风格：极简、冷色调、高级质感

// === 主色调 - iOS 系统冷蓝 ===
export const primaryColor = '#007AFF'; // iOS 标准蓝（冷调）
export const primaryLight = '#5AC8FA'; // 浅冰蓝
export const primaryDark = '#0051D5'; // 深空蓝

// === 功能色 - Apple 系统色 ===
export const successColor = '#34C759'; // Apple 绿 - 正确/完成
export const warningColor = '#FF9500'; // Apple 橙 - 警告/注意
export const errorColor = '#FF3B30'; // Apple 红 - 错误
export const infoColor = '#5AC8FA'; // 冰蓝色 - 信息提示

// === 文字颜色 - Apple 标准 ===
export const textPrimary = '#1D1D1F'; // Apple 黑 - 主要文字
export const textSecondary = '#86868B'; // Apple 中灰 - 次要文字
export const textTertiary = '#C7C7CC'; // Apple 浅灰 - 辅助文字
export const textInverse = '#FFFFFF'; // 白色 - 反色文字

// === 背景色 - Apple 风格灰 ===
export const backgroundPrimary = '#F5F5F7'; // Apple 官网灰
export const backgroundSecondary = '#FAFAFA'; // 次级背景
export const backgroundTertiary = '#F0F0F2'; // 三级背景

// === 卡片与层级 ===
export const cardBackground = '#FFFFFF'; // 卡片纯白背景
export const cardBorder = 'rgba(0, 0, 0, 0.04)'; // 极浅边框（更轻）
export const cardShadowLight = 'rgba(0, 0, 0, 0.02)'; // 轻柔阴影
export const cardShadowMedium = 'rgba(0, 0, 0, 0.04)'; // 中等阴影
export const cardShadowHeavy = 'rgba(0, 0, 0, 0.08)'; // 深层阴影

// === 渐变色组合（微妙冷色调）===
export const gradientPrimary = ['#007AFF', '#5AC8FA']; // 冷蓝渐变
export const gradientSuccess = ['#34C759', '#30D158']; // 绿色渐变
export const gradientWarning = ['#FF9500', '#FFCC00']; // 橙色渐变
export const gradientError = ['#FF3B30', '#FF6B6B']; // 红色渐变
export const gradientInfo = ['#5AC8FA', '#32D6E8']; // 冰蓝渐变
export const gradientSoft = ['#F5F5F7', '#FFFFFF']; // 柔和渐变

// === 辅助冷色 - 用于点缀 ===
export const accentIndigo = '#5856D6'; // 靛蓝
export const accentCyan = '#32D6E8'; // 青色
export const accentTeal = '#5AC8FA'; // 蓝绿
export const accentGray = '#8E8E93'; // 冷灰
export const accentMint = '#00C7BE'; // 薄荷绿

// === 透明度变体 ===
export const primaryAlpha10 = 'rgba(0, 122, 255, 0.1)'; // iOS 蓝 10%
export const primaryAlpha20 = 'rgba(0, 122, 255, 0.2)'; // iOS 蓝 20%
export const primaryAlpha30 = 'rgba(0, 122, 255, 0.3)'; // iOS 蓝 30%
export const successAlpha10 = 'rgba(52, 199, 89, 0.1)'; // Apple 绿 10%
export const errorAlpha10 = 'rgba(255, 59, 48, 0.1)'; // Apple 红 10%
export const warningAlpha10 = 'rgba(255, 149, 0, 0.1)'; // Apple 橙 10%

// === 兼容旧版本 (向后兼容) ===
export const secondaryColor = primaryColor;
export const textColor = textPrimary;
export const secondaryTextColor = textSecondary;
export const backgroundColor = backgroundPrimary;
export const cardBackgroundColor = cardBackground;
export const borderColor = cardBorder;
export const disabledColor = textTertiary;
export const tintColor = primaryColor;
export const systemGray = textSecondary;
export const systemGray2 = textTertiary;
export const systemGray3 = '#C7C7CC'; // Apple 浅灰
export const systemGray4 = '#D1D1D6'; // Apple 极浅灰
export const systemGray5 = '#E5E5EA'; // Apple 超浅灰
export const systemGray6 = '#F2F2F7'; // Apple 背景灰
export const systemBlue = primaryColor; // iOS 蓝
export const systemOrange = warningColor; // Apple 橙
export const systemIndigo = accentIndigo; // 靛蓝
export const systemPurple = '#AF52DE'; // Apple 紫（保留兼容）
export const accentPurple = systemPurple; // 向后兼容
