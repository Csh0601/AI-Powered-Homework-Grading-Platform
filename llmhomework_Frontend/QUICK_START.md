# 🚀 智学伴 UI - 快速入门指南

## 📦 安装与运行

```bash
# 1. 进入前端目录
cd llmhomework_Frontend

# 2. 安装依赖（如果还没安装）
npm install

# 3. 启动项目
npm start

# 或使用特定模式
npm run android  # Android模式
npm run ios      # iOS模式
```

---

## 🎨 使用新的设计系统

### 1️⃣ 导入颜色

```typescript
import {
  // 主色系
  primaryColor,      // '#6366F1' - 蓝紫色
  successColor,      // '#10B981' - 翠绿色
  errorColor,        // '#EF4444' - 珊瑚红
  warningColor,      // '#F59E0B' - 琥珀色

  // 文字色
  textPrimary,       // '#111827' - 深灰黑
  textSecondary,     // '#6B7280' - 中灰色
  textInverse,       // '#FFFFFF' - 白色

  // 背景色
  backgroundPrimary, // '#FFFFFF' - 纯白
  cardBackground,    // '#FFFFFF' - 卡片背景

  // 透明度变体
  primaryAlpha10,    // 主色10%透明度
  successAlpha10,    // 成功色10%透明度
} from './app/styles/colors';
```

### 2️⃣ 导入设计规范

```typescript
import {
  // 间距
  spacing,      // { xs, sm, md, lg, xl, xxl, xxxl }

  // 字体
  typography,   // { heroTitle, displayLarge, heading1, bodyMedium, etc. }

  // 圆角
  borderRadius, // { xs, sm, md, lg, xl, card, button, etc. }

  // 阴影
  shadows,      // { level1, level2, level3, level4 }

  // 尺寸
  sizes,        // { button, icon, avatar, card }
} from './app/styles/designSystem';
```

### 3️⃣ 使用共享组件

```typescript
import { Card, Button, Badge, StatCard } from './app/components/shared';

// 使用Card
<Card variant="elevated" onPress={() => {}}>
  <Text>卡片内容</Text>
</Card>

// 使用Button
<Button
  title="开始学习"
  variant="primary"
  size="large"
  onPress={handlePress}
  fullWidth
/>

// 使用Badge
<Badge label="已完成" variant="success" filled />

// 使用StatCard
<StatCard
  icon="✅"
  value="8/10"
  label="正确题数"
  variant="success"
/>
```

---

## 💡 实用示例

### 示例1：创建一个美观的卡片

```tsx
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Card } from './app/components/shared';
import { typography, spacing, textPrimary, textSecondary } from './app/styles';

const MyCard = () => (
  <Card variant="standard">
    <Text style={styles.title}>我的卡片</Text>
    <Text style={styles.description}>这是一个使用新设计系统的卡片</Text>
  </Card>
);

const styles = StyleSheet.create({
  title: {
    ...typography.heading2,
    color: textPrimary,
    marginBottom: spacing.sm,
  },
  description: {
    ...typography.bodyMedium,
    color: textSecondary,
  },
});
```

### 示例2：创建按钮组

```tsx
import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Button } from './app/components/shared';
import { spacing } from './app/styles/designSystem';

const ButtonGroup = () => (
  <View style={styles.container}>
    <Button title="主要操作" variant="primary" onPress={() => {}} />
    <Button title="次要操作" variant="secondary" onPress={() => {}} />
    <Button title="危险操作" variant="danger" size="medium" onPress={() => {}} />
  </View>
);

const styles = StyleSheet.create({
  container: {
    gap: spacing.md,
    padding: spacing.screenHorizontal,
  },
});
```

### 示例3：创建统计面板

```tsx
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Card, StatCard } from './app/components/shared';
import { typography, spacing, textPrimary } from './app/styles';

const StatsPanel = () => (
  <View style={styles.container}>
    <Text style={styles.title}>学习统计</Text>
    <View style={styles.grid}>
      <StatCard icon="✅" value="85%" label="正确率" variant="success" />
      <StatCard icon="📝" value="120" label="总题数" variant="primary" />
      <StatCard icon="⏱️" value="45m" label="学习时长" variant="warning" />
      <StatCard icon="🔥" value="7" label="连续天数" variant="error" />
    </View>
  </View>
);

const styles = StyleSheet.create({
  container: {
    padding: spacing.screenHorizontal,
  },
  title: {
    ...typography.heading1,
    color: textPrimary,
    marginBottom: spacing.lg,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
});
```

---

## 🎯 样式最佳实践

### ✅ 推荐做法

```typescript
// ✅ 使用设计系统的预设值
const styles = StyleSheet.create({
  container: {
    padding: spacing.screenHorizontal,  // 使用预设间距
    backgroundColor: backgroundPrimary, // 使用预设颜色
    borderRadius: borderRadius.card,    // 使用预设圆角
    ...shadows.level2,                  // 使用预设阴影
  },
  title: {
    ...typography.heading1,             // 使用预设字体样式
    color: textPrimary,
  },
});
```

### ❌ 避免做法

```typescript
// ❌ 硬编码数值
const styles = StyleSheet.create({
  container: {
    padding: 20,                        // 应该用 spacing.lg
    backgroundColor: '#FFFFFF',         // 应该用 backgroundPrimary
    borderRadius: 16,                   // 应该用 borderRadius.md
    shadowOpacity: 0.1,                // 应该用 shadows.level2
  },
  title: {
    fontSize: 24,                      // 应该用 typography.heading1
    fontWeight: '700',
    color: '#000000',                  // 应该用 textPrimary
  },
});
```

---

## 🔄 迁移现有页面

### 步骤1：更新导入

```typescript
// 之前
import {
  primaryColor,
  textColor,
  backgroundColor
} from '../styles/colors';

// 之后（推荐）
import {
  primaryColor,
  textPrimary,      // 替代 textColor
  backgroundPrimary // 替代 backgroundColor
} from '../styles/colors';

// 同时导入设计系统
import { typography, spacing, shadows } from '../styles/designSystem';
```

### 步骤2：替换组件

```typescript
// 之前 - 自定义View
<View style={styles.card}>
  <Text style={styles.title}>标题</Text>
</View>

// 之后 - 使用Card组件
import { Card } from '../components/shared';

<Card variant="standard">
  <Text style={styles.title}>标题</Text>
</Card>
```

### 步骤3：更新样式

```typescript
// 之前
const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 10,
  },
  title: {
    fontSize: 22,
    fontWeight: '700',
    color: '#333',
  },
});

// 之后
const styles = StyleSheet.create({
  title: {
    ...typography.heading2,
    color: textPrimary,
  },
});
// Card的样式已经内置，不需要单独定义
```

---

## 📱 页面布局模板

### 标准页面布局

```tsx
import React from 'react';
import { SafeAreaView, ScrollView, View, Text, StyleSheet } from 'react-native';
import { Card, Button } from '../components/shared';
import {
  backgroundPrimary,
  textPrimary,
  textSecondary,
  typography,
  spacing,
} from '../styles';

const MyScreen = () => {
  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.contentContainer}
        showsVerticalScrollIndicator={false}
      >
        {/* 标题区 */}
        <View style={styles.headerSection}>
          <Text style={styles.title}>页面标题</Text>
          <Text style={styles.subtitle}>页面副标题</Text>
        </View>

        {/* 内容区 */}
        <Card variant="elevated">
          <Text style={styles.cardTitle}>卡片标题</Text>
          <Text style={styles.cardContent}>卡片内容...</Text>
        </Card>

        {/* 操作区 */}
        <View style={styles.actions}>
          <Button title="主要操作" variant="primary" onPress={() => {}} fullWidth />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: backgroundPrimary,
  },
  container: {
    flex: 1,
  },
  contentContainer: {
    paddingHorizontal: spacing.screenHorizontal,
    paddingBottom: spacing.xxxl,
  },
  headerSection: {
    paddingTop: spacing.xl,
    paddingBottom: spacing.xl,
    alignItems: 'center',
  },
  title: {
    ...typography.displayMedium,
    color: textPrimary,
    marginBottom: spacing.sm,
  },
  subtitle: {
    ...typography.bodyLarge,
    color: textSecondary,
  },
  cardTitle: {
    ...typography.heading3,
    color: textPrimary,
    marginBottom: spacing.md,
  },
  cardContent: {
    ...typography.bodyMedium,
    color: textSecondary,
  },
  actions: {
    marginTop: spacing.xl,
  },
});

export default MyScreen;
```

---

## 🐛 常见问题

### Q1: 导入路径错误？
```
Error: Module not found: Can't resolve '../../styles/colors'
```
**解决方案**: 检查你的文件位置，调整相对路径：
- 从 `app/screens/` 导入: `../styles/colors`
- 从 `app/components/shared/` 导入: `../../styles/colors`

### Q2: TypeScript类型错误？
```
Property 'variant' does not exist...
```
**解决方案**: 确保导入了组件类型：
```typescript
import { Card } from '../components/shared';
// 不要用: import Card from '../components/shared/Card';
```

### Q3: 样式不生效？
**解决方案**: 检查是否使用了展开运算符：
```typescript
// ✅ 正确
...typography.heading1

// ❌ 错误
typography.heading1
```

---

## 📚 参考资料

- **设计系统文档**: `DESIGN_SYSTEM.md`
- **错误检查报告**: `ERROR_CHECK_REPORT.md`
- **组件源码**: `app/components/shared/`
- **样式定义**: `app/styles/`

---

## 🎉 开始使用

现在你已经掌握了新设计系统的基础知识！

```bash
# 启动项目看看效果
npm start
```

打开 **UploadScreen** 查看完全重构后的首页效果 🎨

---

💜 让智学伴育莘莘学子 💜

**最后更新**: 2025年10月12日
