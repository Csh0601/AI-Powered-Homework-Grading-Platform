/**
 * 🎨 智学伴 - Apple 风格设计系统
 * 核心理念：让智学伴育莘莘学子
 *
 * 设计原则：
 * 1. 极简克制 - 无渐变、无纹理、冷色调
 * 2. 轻柔阴影 - 仅用于表达层级关系
 * 3. 高对比度 - Apple 标准文字 + 浅灰背景 + 冷蓝高亮
 * 4. 克制圆角 - 12-16px 标准圆角
 * 5. 充足留白 - Apple 风格间距
 * 6. 轻量字体 - 更轻的字重（300-500）
 */

// ============================================
// 📏 间距系统 - Apple 风格留白
// ============================================
export const spacing = {
  // 基础间距
  xs: 4,
  sm: 8,
  md: 16,
  lg: 20,
  xl: 24,
  xxl: 32,
  xxxl: 48,

  // 卡片间距
  cardPadding: 20,
  cardMargin: 16,
  cardGap: 12,

  // 屏幕边距
  screenHorizontal: 20,
  screenVertical: 16,

  // 组件间距
  sectionSpacing: 24,
  elementSpacing: 12,
  itemSpacing: 8,
} as const;

// ============================================
// 🔤 字体系统 - 轻量 Apple 风格
// ============================================
export const typography = {
  // 超大标题 - 轻盈视觉
  heroTitle: {
    fontSize: 48,
    fontWeight: '300' as const,  // 更轻的字重
    letterSpacing: -1.5,
    lineHeight: 56,
  },

  // 大标题
  displayLarge: {
    fontSize: 40,
    fontWeight: '300' as const,  // 轻量
    letterSpacing: -1,
    lineHeight: 48,
  },

  displayMedium: {
    fontSize: 34,
    fontWeight: '400' as const,  // 正常
    letterSpacing: -0.8,
    lineHeight: 42,
  },

  displaySmall: {
    fontSize: 28,
    fontWeight: '400' as const,
    letterSpacing: -0.5,
    lineHeight: 36,
  },

  // 标题
  heading1: {
    fontSize: 24,
    fontWeight: '500' as const,  // 中等
    letterSpacing: -0.3,
    lineHeight: 32,
  },

  heading2: {
    fontSize: 22,
    fontWeight: '500' as const,
    letterSpacing: -0.2,
    lineHeight: 28,
  },

  heading3: {
    fontSize: 20,
    fontWeight: '500' as const,
    letterSpacing: 0,
    lineHeight: 26,
  },

  heading4: {
    fontSize: 18,
    fontWeight: '500' as const,
    letterSpacing: 0,
    lineHeight: 24,
  },

  // 正文
  bodyLarge: {
    fontSize: 17,
    fontWeight: '400' as const,
    letterSpacing: 0,
    lineHeight: 24,
  },

  bodyMedium: {
    fontSize: 15,
    fontWeight: '400' as const,
    letterSpacing: 0,
    lineHeight: 22,
  },

  bodySmall: {
    fontSize: 13,
    fontWeight: '400' as const,
    letterSpacing: 0,
    lineHeight: 18,
  },

  // 标签和说明文字
  caption: {
    fontSize: 12,
    fontWeight: '400' as const,
    letterSpacing: 0,
    lineHeight: 16,
  },

  label: {
    fontSize: 11,
    fontWeight: '500' as const,
    letterSpacing: 0.5,
    lineHeight: 14,
  },

  // 按钮文字
  buttonLarge: {
    fontSize: 17,
    fontWeight: '500' as const,
    letterSpacing: 0,
  },

  buttonMedium: {
    fontSize: 15,
    fontWeight: '500' as const,
    letterSpacing: 0,
  },

  buttonSmall: {
    fontSize: 13,
    fontWeight: '500' as const,
    letterSpacing: 0,
  },
} as const;

// ============================================
// 🎯 圆角系统 - 克制的 Apple 风格
// ============================================
export const borderRadius = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  xxl: 24,
  xxxl: 28,
  full: 9999, // 完全圆形

  // 常用场景
  button: 12,       // 按钮统一12px
  card: 16,         // 卡片统一16px
  cardLarge: 20,    // 大卡片20px
  input: 10,        // 输入框10px
  badge: 12,        // 徽章12px
  chip: 18,         // 胶囊18px
} as const;

// ============================================
// 💫 阴影系统 - 轻柔 Apple 风格
// ============================================
export const shadows = {
  // 轻微抬起 (1层) - 极轻
  level1: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.02,
    shadowRadius: 2,
    elevation: 1,
  },

  // 中等抬起 (2层) - 轻柔
  level2: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 4,
    elevation: 2,
  },

  // 明显抬起 (3层) - 中等
  level3: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 4,
  },

  // 高层悬浮 (4层) - 明显
  level4: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.08,
    shadowRadius: 12,
    elevation: 6,
  },

  // 最高层 (模态/浮层) - 深层
  modal: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.12,
    shadowRadius: 16,
    elevation: 8,
  },
} as const;

// ============================================
// 🎭 动画配置
// ============================================
export const animations = {
  // 时长
  duration: {
    fast: 200,
    normal: 300,
    slow: 400,
    verySlow: 600,
  },

  // 缓动函数
  easing: {
    easeInOut: [0.4, 0, 0.2, 1],
    easeOut: [0, 0, 0.2, 1],
    easeIn: [0.4, 0, 1, 1],
    spring: [0.68, -0.55, 0.265, 1.55],
  },
} as const;

// ============================================
// 📐 组件尺寸规范 - Apple 标准
// ============================================
export const sizes = {
  // 按钮高度
  button: {
    small: 32,
    medium: 44,      // iOS 标准触控高度
    large: 50,
    xlarge: 56,
  },

  // 输入框高度
  input: {
    small: 36,
    medium: 44,      // iOS 标准
    large: 50,
  },

  // 图标尺寸
  icon: {
    xs: 16,
    sm: 20,
    md: 24,          // 标准尺寸
    lg: 28,
    xl: 32,
    xxl: 40,
  },

  // 头像尺寸
  avatar: {
    small: 32,
    medium: 44,
    large: 56,
    xlarge: 72,
  },

  // 卡片最小高度
  card: {
    small: 100,
    medium: 140,
    large: 180,
  },
} as const;

// ============================================
// 🎨 预设卡片样式
// ============================================
export const cardStyles = {
  // 标准卡片
  standard: {
    backgroundColor: '#FFFFFF',
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding,
    ...shadows.level2,
  },

  // 大卡片
  large: {
    backgroundColor: '#FFFFFF',
    borderRadius: borderRadius.cardLarge,
    padding: spacing.xl,
    ...shadows.level3,
  },

  // 紧凑卡片
  compact: {
    backgroundColor: '#FFFFFF',
    borderRadius: borderRadius.md,
    padding: spacing.md,
    ...shadows.level1,
  },

  // 悬浮卡片
  elevated: {
    backgroundColor: '#FFFFFF',
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding,
    ...shadows.level4,
  },
} as const;

// ============================================
// 🎯 预设按钮样式
// ============================================
export const buttonStyles = {
  // 主要按钮
  primary: {
    height: sizes.button.large,
    borderRadius: borderRadius.button,
    paddingHorizontal: spacing.xl,
    ...shadows.level2,
  },

  // 次要按钮
  secondary: {
    height: sizes.button.medium,
    borderRadius: borderRadius.button,
    paddingHorizontal: spacing.lg,
    ...shadows.level1,
  },

  // 小按钮
  small: {
    height: sizes.button.small,
    borderRadius: borderRadius.sm,
    paddingHorizontal: spacing.md,
  },
} as const;

// ============================================
// 📊 常用数值
// ============================================
export const constants = {
  // 最大内容宽度
  maxContentWidth: 480,

  // 列表项高度
  listItemHeight: 64,

  // 导航栏高度
  headerHeight: 44,    // iOS 标准

  // 底部导航高度
  tabBarHeight: 50,    // iOS 标准

  // 安全区域
  safeAreaPadding: 16,
} as const;

/**
 * 辅助函数：创建响应式间距
 */
export const responsiveSpacing = (baseSpacing: number) => ({
  small: baseSpacing * 0.75,
  medium: baseSpacing,
  large: baseSpacing * 1.25,
});

/**
 * 辅助函数：创建响应式字体
 */
export const responsiveFontSize = (baseFontSize: number) => ({
  small: baseFontSize * 0.875,
  medium: baseFontSize,
  large: baseFontSize * 1.125,
});
