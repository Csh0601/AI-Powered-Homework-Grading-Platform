/**
 * 🔘 智学伴 - 通用按钮组件
 * Apple 冷色调风格 - 纯色背景 + 轻柔阴影
 */

import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ViewStyle, TextStyle, ActivityIndicator } from 'react-native';
import {
  primaryColor,
  textInverse,
  textPrimary,
  successColor,
  errorColor,
  warningColor,
  primaryAlpha10,
  cardBackground
} from '../../styles/colors';
import { borderRadius, shadows, typography, sizes } from '../../styles/designSystem';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'ghost';
  size?: 'small' | 'medium' | 'large' | 'xlarge';
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  size = 'large',
  disabled = false,
  loading = false,
  fullWidth = false,
  style,
  textStyle,
  icon,
}) => {
  const buttonStyle = [
    styles.base,
    styles[variant],
    styles[`size_${size}`],
    fullWidth && styles.fullWidth,
    disabled && styles.disabled,
    style,
  ];

  const titleStyle = [
    styles.text,
    styles[`text_${variant}`],
    styles[`textSize_${size}`],
    disabled && styles.textDisabled,
    textStyle,
  ];

  return (
    <TouchableOpacity
      style={buttonStyle}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.7}
    >
      {loading ? (
        <ActivityIndicator color={variant === 'ghost' || variant === 'secondary' ? primaryColor : textInverse} />
      ) : (
        <>
          {icon}
          <Text style={titleStyle}>{title}</Text>
        </>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  base: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    borderRadius: borderRadius.button,
  },

  // 变体样式 - 纯色风格
  primary: {
    backgroundColor: primaryColor,
    ...shadows.level2,
  },

  secondary: {
    backgroundColor: cardBackground,
    borderWidth: 1,
    borderColor: primaryColor,
    ...shadows.level1,
  },

  success: {
    backgroundColor: successColor,
    ...shadows.level2,
  },

  danger: {
    backgroundColor: errorColor,
    ...shadows.level2,
  },

  warning: {
    backgroundColor: warningColor,
    ...shadows.level2,
  },

  ghost: {
    backgroundColor: primaryAlpha10,
  },

  // 尺寸样式 - iOS 标准
  size_small: {
    height: sizes.button.small,
    paddingHorizontal: 16,
  },

  size_medium: {
    height: sizes.button.medium,
    paddingHorizontal: 20,
  },

  size_large: {
    height: sizes.button.large,
    paddingHorizontal: 24,
  },

  size_xlarge: {
    height: sizes.button.xlarge,
    paddingHorizontal: 32,
  },

  fullWidth: {
    width: '100%',
  },

  disabled: {
    opacity: 0.4,
  },

  // 文字样式
  text: {
    textAlign: 'center',
  },

  text_primary: {
    color: textInverse,
    ...typography.buttonLarge,
  },

  text_secondary: {
    color: primaryColor,
    ...typography.buttonLarge,
  },

  text_success: {
    color: textInverse,
    ...typography.buttonLarge,
  },

  text_danger: {
    color: textInverse,
    ...typography.buttonLarge,
  },

  text_warning: {
    color: textInverse,
    ...typography.buttonLarge,
  },

  text_ghost: {
    color: primaryColor,
    ...typography.buttonMedium,
  },

  textSize_small: {
    ...typography.buttonSmall,
  },

  textSize_medium: {
    ...typography.buttonMedium,
  },

  textSize_large: {
    ...typography.buttonLarge,
  },

  textSize_xlarge: {
    fontSize: 18,
    fontWeight: '500',
  },

  textDisabled: {
    opacity: 1,
  },
});
