import { RouteProp, useRoute } from '@react-navigation/native';
import React from 'react';
import { FlatList, SafeAreaView, StyleSheet, Text, View } from 'react-native';
import { RootStackParamList } from '../navigation/NavigationTypes';
import {
  textPrimary,
  textSecondary,
  backgroundPrimary,
  cardBackground,
  borderColor,
  primaryAlpha10
} from '../styles/colors';
import { typography, spacing, borderRadius, shadows } from '../styles/designSystem';

type SuggestionsRouteProp = RouteProp<RootStackParamList, 'StudySuggestions'>;

const StudySuggestionsScreen: React.FC = () => {
  const route = useRoute<SuggestionsRouteProp>();
  
  // 打印调试信息
  console.log('🔍 StudySuggestionsScreen 接收到的参数:', {
    suggestions: route.params?.suggestions,
    practiceQuestions: route.params?.practiceQuestions,
    learningSuggestions: route.params?.learningSuggestions,
    summaryLearningSuggestions: route.params?.summaryLearningSuggestions
  });
  
  const suggestions = route.params?.suggestions ?? [];
  const practiceQuestions = route.params?.practiceQuestions ?? [];
  const learningSuggestions = route.params?.learningSuggestions ?? [];
  const summaryLearningSuggestions = route.params?.summaryLearningSuggestions ?? [];
  
  // 合并所有学习建议
  const allSuggestions = [
    ...suggestions,
    ...learningSuggestions,
    ...summaryLearningSuggestions
  ].filter((item, index, array) => {
    // 去重：保留第一次出现的建议
    return array.indexOf(item) === index && item && typeof item === 'string' && item.trim().length > 0;
  });

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <Text style={styles.sectionTitle}>学习建议</Text>
        <FlatList
          data={allSuggestions}
          keyExtractor={(item, index) => `suggestion-${index}`}
          renderItem={({ item, index }) => (
            <View style={styles.suggestionCard}>
              <View style={styles.suggestionHeader}>
                <View style={styles.suggestionIconContainer}>
                  <Text style={styles.suggestionIcon}>💡</Text>
                </View>
                <Text style={styles.suggestionTitle}>建议 {index + 1}</Text>
              </View>
              <Text style={styles.suggestionContent}>{item}</Text>
            </View>
          )}
          ListEmptyComponent={
            <View style={styles.emptyCard}>
              <Text style={styles.emptyText}>暂无具体学习建议，表现出色！</Text>
            </View>
          }
          contentContainerStyle={allSuggestions.length ? undefined : styles.centerContent}
        />
        
        {/* 显示学习建议统计信息 */}
        {allSuggestions.length > 0 && (
          <View style={styles.statsCard}>
            <Text style={styles.statsTitle}>建议来源统计</Text>
            <View style={styles.statsContent}>
              {suggestions.length > 0 && (
                <Text style={styles.statsItem}>• 系统分析建议: {suggestions.length} 条</Text>
              )}
              {learningSuggestions.length > 0 && (
                <Text style={styles.statsItem}>• 题目针对性建议: {learningSuggestions.length} 条</Text>
              )}
              {summaryLearningSuggestions.length > 0 && (
                <Text style={styles.statsItem}>• 整体学习建议: {summaryLearningSuggestions.length} 条</Text>
              )}
            </View>
          </View>
        )}

        <Text style={[styles.sectionTitle, styles.practiceTitle]}>推荐练习</Text>
        {practiceQuestions.length > 0 ? (
          practiceQuestions.map((item: any, index: number) => (
            <View key={index} style={styles.practiceCard}>
              <Text style={styles.practiceHeader}>练习题 {index + 1}</Text>
              <Text style={styles.practiceContent}>{item.text || '练习题内容'}</Text>
            </View>
          ))
        ) : (
          <View style={styles.emptyCard}>
            <Text style={styles.emptyText}>暂无推荐练习题，可以继续巩固当前知识点。</Text>
          </View>
        )}
      </View>
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
    padding: spacing.screenHorizontal,
  },
  sectionTitle: {
    ...typography.heading2,
    fontWeight: '500',  // Apple 中等字重
    color: textPrimary,
    marginBottom: spacing.lg,
  },
  suggestionCard: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding,
    marginBottom: spacing.md,
    borderWidth: 0.5,  // Apple 精细边框
    borderColor: borderColor,
    ...shadows.level1,  // 轻柔阴影
  },
  suggestionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  suggestionIconContainer: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: primaryAlpha10,  // 移除紫色调
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.sm,
  },
  suggestionIcon: {
    fontSize: 16,
  },
  suggestionTitle: {
    ...typography.bodyMedium,
    fontWeight: '500',
    color: textPrimary,
  },
  suggestionContent: {
    ...typography.bodySmall,
    color: textSecondary,
    lineHeight: 20,
    paddingLeft: 40,
  },
  statsCard: {
    backgroundColor: primaryAlpha10,  // 移除紫色调
    borderRadius: borderRadius.md,
    padding: spacing.cardPadding,
    marginVertical: spacing.lg,
    borderWidth: 0.5,
    borderColor: borderColor,
  },
  statsTitle: {
    ...typography.bodySmall,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.sm,
  },
  statsContent: {
    gap: spacing.xs,
  },
  statsItem: {
    ...typography.caption,
    color: textSecondary,
    lineHeight: 18,
  },
  emptyCard: {
    backgroundColor: primaryAlpha10,
    padding: spacing.cardPadding,
    borderRadius: borderRadius.md,
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  emptyText: {
    ...typography.bodySmall,
    color: textSecondary,
  },
  centerContent: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  practiceTitle: {
    marginTop: spacing.xl,
  },
  practiceCard: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding,
    marginBottom: spacing.md,
    borderWidth: 0.5,
    borderColor: borderColor,
  },
  practiceHeader: {
    ...typography.bodyMedium,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.xs,
  },
  practiceContent: {
    ...typography.bodySmall,
    color: textSecondary,
    lineHeight: 20,
  },
});

export default StudySuggestionsScreen;

