/**
 * 🎯 智学伴 - IconButton 组件
 * Apple 冷色调风格 - 替代 DecorativeButton
 */

import React from 'react';
import { TouchableOpacity, StyleSheet, ViewStyle } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import {
  primaryColor,
  textSecondary,
  cardBackground,
  primaryAlpha10,
  accentGray,
} from '../../styles/colors';
import { shadows, sizes } from '../../styles/designSystem';

interface IconButtonProps {
  iconName: keyof typeof Ionicons.glyphMap;
  onPress: () => void;
  size?: 'small' | 'medium' | 'large';
  variant?: 'primary' | 'secondary' | 'ghost';
  disabled?: boolean;
  style?: ViewStyle;
}

export const IconButton: React.FC<IconButtonProps> = ({
  iconName,
  onPress,
  size = 'medium',
  variant = 'primary',
  disabled = false,
  style,
}) => {
  const buttonSize = size === 'small' ? 40 : size === 'large' ? 56 : 48;
  const iconSize = size === 'small' ? 20 : size === 'large' ? 28 : 24;

  const buttonStyle = [
    styles.base,
    { width: buttonSize, height: buttonSize, borderRadius: buttonSize / 2 },
    variant === 'primary' && styles.primary,
    variant === 'secondary' && styles.secondary,
    variant === 'ghost' && styles.ghost,
    disabled && styles.disabled,
    style,
  ];

  const iconColor =
    variant === 'primary'
      ? '#FFFFFF'
      : variant === 'ghost'
      ? accentGray
      : primaryColor;

  return (
    <TouchableOpacity
      style={buttonStyle}
      onPress={onPress}
      disabled={disabled}
      activeOpacity={0.7}
    >
      <Ionicons name={iconName} size={iconSize} color={iconColor} />
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  base: {
    alignItems: 'center',
    justifyContent: 'center',
  },

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

  ghost: {
    backgroundColor: primaryAlpha10,
  },

  disabled: {
    opacity: 0.4,
  },
});
