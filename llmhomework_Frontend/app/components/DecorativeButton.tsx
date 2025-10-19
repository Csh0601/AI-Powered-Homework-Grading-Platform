import React from 'react';
import { TouchableOpacity, View, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

interface DecorativeButtonProps {
  onPress?: () => void;
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  iconName?: keyof typeof Ionicons.glyphMap;
  gradientColors?: readonly [string, string, ...string[]];
  borderColor?: string;
  outerColor?: string;
}

const DecorativeButton: React.FC<DecorativeButtonProps> = ({ 
  onPress, 
  size = 'md',
  disabled = false,
  iconName = 'settings',
  gradientColors = ['#4ade80', '#14b8a6'],
  borderColor = '#92400e',
  outerColor = '#d97706'
}) => {
  const sizeConfig = {
    sm: { 
      containerSize: 48, 
      iconSize: 20,
      borderWidth: 3 
    },
    md: { 
      containerSize: 64, 
      iconSize: 24,
      borderWidth: 4 
    },
    lg: { 
      containerSize: 80, 
      iconSize: 28,
      borderWidth: 5 
    }
  };

  const config = sizeConfig[size];

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled}
      activeOpacity={0.8}
      style={[
        styles.container,
        {
          width: config.containerSize,
          height: config.containerSize,
        },
        disabled && styles.disabled
      ]}
    >
      {/* Outer decorative border */}
      <View 
        style={[
          styles.outerBorder,
          {
            width: config.containerSize,
            height: config.containerSize,
            borderRadius: config.containerSize / 4,
            backgroundColor: outerColor,
          }
        ]}
      >
        {/* Inner border with gradient - 使用绝对定位确保居中 */}
        <View 
          style={[
            styles.innerBorder,
            {
              width: config.containerSize - 8,
              height: config.containerSize - 8,
              borderRadius: (config.containerSize - 8) / 4,
              borderWidth: config.borderWidth,
              borderColor: borderColor,
            }
          ]}
        >
          <LinearGradient
            colors={gradientColors}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={[
              styles.gradient,
              {
                width: config.containerSize - 16,
                height: config.containerSize - 16,
                borderRadius: (config.containerSize - 16) / 4,
              }
            ]}
          >
            <Ionicons 
              name={iconName}
              size={config.iconSize} 
              color="white"
              style={styles.icon}
            />
          </LinearGradient>
        </View>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  outerBorder: {
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#92400e',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 8,
  },
  innerBorder: {
    backgroundColor: '#f59e0b',
    alignItems: 'center',
    justifyContent: 'center',
  },
  gradient: {
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.2,
    shadowRadius: 2,
    elevation: 4,
  },
  icon: {
    textAlign: 'center',
    textShadowColor: 'rgba(0, 0, 0, 0.3)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 2,
  },
  disabled: {
    opacity: 0.5,
  },
});

export { DecorativeButton };
