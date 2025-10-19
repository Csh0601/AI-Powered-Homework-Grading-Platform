/**
 * 💊 智学伴 - 胶囊按钮组件
 * Apple 风格 Capsule Button - 用于功能入口
 */

import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ViewStyle } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import {
  primaryColor,
  primaryAlpha10,
  textPrimary,
  cardBackground,
} from '../../styles/colors';
import { typography, borderRadius, spacing } from '../../styles/designSystem';

interface CapsuleButtonProps {
  title: string;
  iconName: keyof typeof Ionicons.glyphMap;
  onPress: () => void;
  variant?: 'filled' | 'outline';
  disabled?: boolean;
  style?: ViewStyle;
}

export const CapsuleButton: React.FC<CapsuleButtonProps> = ({
  title,
  iconName,
  onPress,
  variant = 'outline',
  disabled = false,
  style,
}) => {
  const buttonStyle = [
    styles.base,
    variant === 'filled' ? styles.filled : styles.outline,
    disabled && styles.disabled,
    style,
  ];

  const textColor = variant === 'filled' ? '#FFFFFF' : primaryColor;
  const iconColor = variant === 'filled' ? '#FFFFFF' : primaryColor;

  return (
    <TouchableOpacity
      style={buttonStyle}
      onPress={onPress}
      disabled={disabled}
      activeOpacity={0.7}
    >
      <Ionicons name={iconName} size={16} color={iconColor} />
      <Text style={[styles.text, { color: textColor }]}>{title}</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  base: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.full,
    gap: spacing.xs,
  },

  filled: {
    backgroundColor: primaryColor,
  },

  outline: {
    backgroundColor: primaryAlpha10,
    borderWidth: 1,
    borderColor: primaryColor,
  },

  disabled: {
    opacity: 0.4,
  },

  text: {
    ...typography.caption,
    fontWeight: '500',
  },
});
