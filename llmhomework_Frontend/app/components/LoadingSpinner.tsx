import React from 'react';
import { ActivityIndicator, StyleSheet, Text, View, Animated } from 'react-native';
import { 
  primaryColor, 
  textColor, 
  secondaryTextColor, 
  backgroundColor,
  cardBackgroundColor
} from '../styles/colors';

interface LoadingSpinnerProps {
  text?: string;
  size?: 'small' | 'large';
  color?: string;
  variant?: 'default' | 'card' | 'minimal';
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  text = '加载中...', 
  size = 'large', 
  color = primaryColor,
  variant = 'default'
}) => {
  return (
    <View style={[styles.container, styles[variant]]}>
      <View style={styles.spinnerContainer}>
        <ActivityIndicator size={size} color={color} />
      </View>
      {text && (
        <Text style={[styles.text, styles[`${variant}Text`]]}>
          {text}
        </Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  default: {
    backgroundColor: backgroundColor,
  },
  card: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 16,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.08,
    shadowRadius: 12,
    elevation: 4,
  },
  minimal: {
    padding: 16,
  },
  spinnerContainer: {
    marginBottom: 16,
  },
  text: {
    fontSize: 16,
    fontWeight: '500',
    textAlign: 'center',
  },
  defaultText: {
    color: textColor,
  },
  cardText: {
    color: textColor,
    fontSize: 16,
    fontWeight: '600',
  },
  minimalText: {
    color: secondaryTextColor,
    fontSize: 14,
  },
});

export default LoadingSpinner;
