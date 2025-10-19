/**
 * 📊 智学伴 - 统计卡片组件
 * 用于展示数字统计信息
 */

import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { Card } from './Card';
import {
  textPrimary,
  textSecondary,
  primaryColor,
  successColor,
  errorColor,
  warningColor,
  primaryAlpha10,
  successAlpha10,
  errorAlpha10,
  warningAlpha10,
} from '../../styles/colors';
import { typography, spacing, sizes } from '../../styles/designSystem';

interface StatCardProps {
  icon?: string;
  value: string | number;
  label: string;
  variant?: 'primary' | 'success' | 'error' | 'warning' | 'neutral';
  style?: ViewStyle;
  size?: 'small' | 'medium' | 'large';
}

export const StatCard: React.FC<StatCardProps> = ({
  icon,
  value,
  label,
  variant = 'primary',
  style,
  size = 'medium',
}) => {
  const colorMap = {
    primary: primaryColor,
    success: successColor,
    error: errorColor,
    warning: warningColor,
    neutral: textPrimary,
  };

  const bgColorMap = {
    primary: primaryAlpha10,
    success: successAlpha10,
    error: errorAlpha10,
    warning: warningAlpha10,
    neutral: 'rgba(0, 0, 0, 0.05)',
  };

  return (
    <Card variant="compact" style={style}>
      {/* 图标容器 */}
      {icon && (
        <View
          style={[
            styles.iconContainer,
            { backgroundColor: bgColorMap[variant] },
            styles[`iconSize_${size}`],
          ]}
        >
          <Text style={[styles.icon, styles[`iconText_${size}`]]}>{icon}</Text>
        </View>
      )}

      {/* 数值 */}
      <Text
        style={[
          styles.value,
          { color: colorMap[variant] },
          styles[`valueSize_${size}`],
        ]}
      >
        {value}
      </Text>

      {/* 标签 */}
      <Text style={[styles.label, styles[`labelSize_${size}`]]}>{label}</Text>
    </Card>
  );
};

const styles = StyleSheet.create({
  iconContainer: {
    borderRadius: 999,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
  },

  iconSize_small: {
    width: sizes.icon.lg,
    height: sizes.icon.lg,
  },

  iconSize_medium: {
    width: sizes.icon.xl,
    height: sizes.icon.xl,
  },

  iconSize_large: {
    width: sizes.icon.xxl,
    height: sizes.icon.xxl,
  },

  icon: {},

  iconText_small: {
    fontSize: 20,
  },

  iconText_medium: {
    fontSize: 24,
  },

  iconText_large: {
    fontSize: 28,
  },

  value: {
    ...typography.displaySmall,
    marginBottom: spacing.xs,
  },

  valueSize_small: {
    fontSize: 24,
    fontWeight: '700',
  },

  valueSize_medium: {
    fontSize: 32,
    fontWeight: '800',
  },

  valueSize_large: {
    fontSize: 40,
    fontWeight: '900',
  },

  label: {
    ...typography.bodyMedium,
    color: textSecondary,
    textAlign: 'center',
  },

  labelSize_small: {
    fontSize: 12,
  },

  labelSize_medium: {
    fontSize: 14,
  },

  labelSize_large: {
    fontSize: 16,
  },
});
