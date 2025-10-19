import { RouteProp, useNavigation, useRoute } from '@react-navigation/native';
import React from 'react';
import { SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';
import LaTeXRenderer from '../components/LaTeXRenderer';
import { RootStackParamList } from '../navigation/NavigationTypes';
import {
  textPrimary,
  textSecondary,
  backgroundPrimary,
  cardBackground,
  borderColor
} from '../styles/colors';
import { typography, spacing, borderRadius, shadows } from '../styles/designSystem';

type ExplanationRouteProp = RouteProp<RootStackParamList, 'Explanation'>;

const ExplanationScreen: React.FC = () => {
  const route = useRoute<ExplanationRouteProp>();
  const navigation = useNavigation();

  const result = route.params?.result ?? {};

  const hasLaTeX = (text: string): boolean => {
    if (!text) return false;
    return /\frac|\times|\div|\^|_|\\[a-zA-Z]+/.test(text);
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>题目</Text>
          <View style={styles.card}>
            <ScrollView
              style={styles.cardScroll}
              contentContainerStyle={styles.cardScrollContent}
              nestedScrollEnabled
            >
              {hasLaTeX(result.question) ? (
                <LaTeXRenderer content={result.question} fontSize={18} color={textPrimary} />
              ) : (
                <Text style={styles.text}>{result.question || '题目内容缺失'}</Text>
              )}
            </ScrollView>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>学生答案</Text>
          <View style={styles.card}>
            <ScrollView
              style={styles.cardScroll}
              contentContainerStyle={styles.cardScrollContent}
              nestedScrollEnabled
            >
              {hasLaTeX(result.userAnswer) ? (
                <LaTeXRenderer content={result.userAnswer} fontSize={16} color={textPrimary} />
              ) : (
                <Text style={styles.text}>{result.userAnswer || '未作答'}</Text>
              )}
            </ScrollView>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>正确答案</Text>
          <View style={styles.card}>
            <ScrollView
              style={styles.cardScroll}
              contentContainerStyle={styles.cardScrollContent}
              nestedScrollEnabled
            >
              {hasLaTeX(result.correctAnswer) ? (
                <LaTeXRenderer content={result.correctAnswer} fontSize={16} color={textPrimary} />
              ) : (
                <Text style={styles.text}>{result.correctAnswer || '参考答案缺失'}</Text>
              )}
            </ScrollView>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>解析</Text>
          <View style={styles.card}>
            <ScrollView
              style={styles.cardScroll}
              contentContainerStyle={styles.cardScrollContent}
              nestedScrollEnabled
            >
              {hasLaTeX(result.explanation) ? (
                <LaTeXRenderer content={result.explanation} fontSize={15} color={textSecondary} />
              ) : (
                <Text style={[styles.text, styles.detailText]}>
                  {result.explanation || '暂无解析'}
                </Text>
              )}
            </ScrollView>
          </View>
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
    padding: spacing.screenHorizontal,
    paddingBottom: spacing.xxxl + spacing.md,
  },
  section: {
    marginBottom: spacing.xl,
  },
  sectionTitle: {
    ...typography.heading3,
    fontWeight: '500',  // Apple 中等字重
    color: textPrimary,
    marginBottom: spacing.md,
  },
  card: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding,
    borderWidth: 0.5,  // Apple 精细边框
    borderColor: borderColor,
    ...shadows.level2,  // 轻柔阴影
    maxHeight: 220,
  },
  text: {
    ...typography.bodyMedium,
    color: textPrimary,
    lineHeight: 24,
  },
  detailText: {
    color: textSecondary,
  },
  cardScroll: {
    maxHeight: 200,
  },
  cardScrollContent: {
    paddingRight: spacing.xs,
  },
});

export default ExplanationScreen;

