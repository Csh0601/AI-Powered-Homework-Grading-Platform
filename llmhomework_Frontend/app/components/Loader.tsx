// Loader.tsx
import React, { useRef, useEffect } from 'react';
import { View, Animated, Easing, StyleSheet } from 'react-native';

interface LoaderProps {
  size?: number;
  color?: string;
  spacing?: number;
}

const Loader: React.FC<LoaderProps> = ({ size = 12, color = '#4F46E5', spacing = 8 }) => {
  const scales = [
    useRef(new Animated.Value(0.3)).current,
    useRef(new Animated.Value(0.3)).current,
    useRef(new Animated.Value(0.3)).current
  ];

  useEffect(() => {
    scales.forEach((scale, index) => {
      const animate = () => {
        Animated.sequence([
          Animated.timing(scale, {
            toValue: 1,
            duration: 400,
            delay: index * 150,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
          Animated.timing(scale, {
            toValue: 0.3,
            duration: 400,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
        ]).start(() => animate());
      };
      animate();
    });
  }, [scales]);

  return (
    <View style={[styles.container, { gap: spacing }]}>
      {scales.map((scale, i) => (
        <Animated.View
          key={i}
          style={[
            styles.dot,
            {
              width: size,
              height: size,
              backgroundColor: color,
              transform: [{ scale }],
            },
          ]}
        />
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  dot: {
    borderRadius: 9999,
  },
});

export default Loader;
