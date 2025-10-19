/**
 * 🏷️ 智学伴 - 徽章组件
 * 用于显示状态、标签等
 */

import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import {
  primaryColor,
  successColor,
  errorColor,
  warningColor,
  textInverse,
  primaryAlpha10,
  successAlpha10,
  errorAlpha10,
  warningAlpha10,
  textSecondary,
} from '../../styles/colors';
import { borderRadius, typography } from '../../styles/designSystem';

interface BadgeProps {
  label: string;
  variant?: 'primary' | 'success' | 'error' | 'warning' | 'neutral';
  size?: 'small' | 'medium' | 'large';
  style?: ViewStyle;
  filled?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  label,
  variant = 'neutral',
  size = 'medium',
  style,
  filled = false,
}) => {
  const badgeStyle = [
    styles.base,
    filled ? styles[`filled_${variant}`] : styles[`outlined_${variant}`],
    styles[`size_${size}`],
    style,
  ];

  const textStyle = [
    styles.text,
    filled ? styles[`textFilled_${variant}`] : styles[`textOutlined_${variant}`],
    styles[`textSize_${size}`],
  ];

  return (
    <View style={badgeStyle}>
      <Text style={textStyle}>{label}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  base: {
    alignSelf: 'flex-start',
    borderRadius: borderRadius.badge,
    borderWidth: 1.5,
  },

  // Filled 变体
  filled_primary: {
    backgroundColor: primaryColor,
    borderColor: primaryColor,
  },

  filled_success: {
    backgroundColor: successColor,
    borderColor: successColor,
  },

  filled_error: {
    backgroundColor: errorColor,
    borderColor: errorColor,
  },

  filled_warning: {
    backgroundColor: warningColor,
    borderColor: warningColor,
  },

  filled_neutral: {
    backgroundColor: textSecondary,
    borderColor: textSecondary,
  },

  // Outlined 变体
  outlined_primary: {
    backgroundColor: primaryAlpha10,
    borderColor: primaryColor,
  },

  outlined_success: {
    backgroundColor: successAlpha10,
    borderColor: successColor,
  },

  outlined_error: {
    backgroundColor: errorAlpha10,
    borderColor: errorColor,
  },

  outlined_warning: {
    backgroundColor: warningAlpha10,
    borderColor: warningColor,
  },

  outlined_neutral: {
    backgroundColor: 'transparent',
    borderColor: textSecondary,
  },

  // 尺寸
  size_small: {
    paddingHorizontal: 8,
    paddingVertical: 4,
  },

  size_medium: {
    paddingHorizontal: 12,
    paddingVertical: 6,
  },

  size_large: {
    paddingHorizontal: 16,
    paddingVertical: 8,
  },

  // 文字样式
  text: {
    ...typography.label,
  },

  textFilled_primary: {
    color: textInverse,
  },

  textFilled_success: {
    color: textInverse,
  },

  textFilled_error: {
    color: textInverse,
  },

  textFilled_warning: {
    color: textInverse,
  },

  textFilled_neutral: {
    color: textInverse,
  },

  textOutlined_primary: {
    color: primaryColor,
  },

  textOutlined_success: {
    color: successColor,
  },

  textOutlined_error: {
    color: errorColor,
  },

  textOutlined_warning: {
    color: warningColor,
  },

  textOutlined_neutral: {
    color: textSecondary,
  },

  textSize_small: {
    fontSize: 11,
  },

  textSize_medium: {
    fontSize: 12,
  },

  textSize_large: {
    fontSize: 14,
  },
});
