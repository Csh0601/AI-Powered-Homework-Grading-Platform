/**
 * 🎴 智学伴 - 通用卡片组件
 * Apple 冷色调风格 - 纯白背景 + 轻柔阴影
 */

import React from 'react';
import { View, StyleSheet, ViewStyle, TouchableOpacity } from 'react-native';
import { cardBackground, cardBorder } from '../../styles/colors';
import { borderRadius, shadows, spacing } from '../../styles/designSystem';

interface CardProps {
  children: React.ReactNode;
  variant?: 'standard' | 'large' | 'compact' | 'elevated';
  onPress?: () => void;
  style?: ViewStyle;
  noPadding?: boolean;
  noShadow?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'standard',
  onPress,
  style,
  noPadding = false,
  noShadow = false,
}) => {
  const cardStyle = [
    styles.base,
    styles[variant],
    noPadding && styles.noPadding,
    noShadow && styles.noShadow,
    style,
  ];

  if (onPress) {
    return (
      <TouchableOpacity
        style={cardStyle}
        onPress={onPress}
        activeOpacity={0.8}
      >
        {children}
      </TouchableOpacity>
    );
  }

  return <View style={cardStyle}>{children}</View>;
};

const styles = StyleSheet.create({
  base: {
    backgroundColor: cardBackground,
    borderWidth: 0.5,          // 更轻的边框
    borderColor: cardBorder,
    overflow: 'hidden',
  },

  // 标准卡片 - 轻柔阴影
  standard: {
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding,
    ...shadows.level2,
  },

  // 大卡片 - 更多内边距
  large: {
    borderRadius: borderRadius.cardLarge,
    padding: spacing.xl,
    ...shadows.level2,           // 使用level2替代level3，更轻柔
  },

  // 紧凑卡片 - 更小内边距
  compact: {
    borderRadius: borderRadius.md,
    padding: spacing.md,
    ...shadows.level1,
  },

  // 悬浮卡片 - 更明显阴影
  elevated: {
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding,
    ...shadows.level3,           // 使用level3替代level4
  },

  noPadding: {
    padding: 0,
  },

  noShadow: {
    shadowColor: 'transparent',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0,
    shadowRadius: 0,
    elevation: 0,
  },
});
