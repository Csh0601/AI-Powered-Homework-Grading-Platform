import { RouteProp, useRoute } from '@react-navigation/native';
import React from 'react';
import { FlatList, SafeAreaView, StyleSheet, Text, View } from 'react-native';
import { RootStackParamList } from '../navigation/NavigationTypes';
import { cardBackgroundColor, secondaryTextColor, textColor } from '../styles/colors';

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
    backgroundColor: '#F5F5FF',
  },
  container: {
    flex: 1,
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: textColor,
    marginBottom: 16,
  },
  suggestionCard: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.05)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  suggestionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  suggestionIconContainer: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: 'rgba(88, 86, 214, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
  },
  suggestionIcon: {
    fontSize: 16,
  },
  suggestionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: textColor,
  },
  suggestionContent: {
    fontSize: 14,
    color: secondaryTextColor,
    lineHeight: 20,
    paddingLeft: 40,
  },
  statsCard: {
    backgroundColor: 'rgba(88, 86, 214, 0.05)',
    borderRadius: 12,
    padding: 16,
    marginVertical: 16,
    borderWidth: 1,
    borderColor: 'rgba(88, 86, 214, 0.1)',
  },
  statsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: textColor,
    marginBottom: 8,
  },
  statsContent: {
    gap: 4,
  },
  statsItem: {
    fontSize: 12,
    color: secondaryTextColor,
    lineHeight: 18,
  },
  emptyCard: {
    backgroundColor: 'rgba(0,0,0,0.03)',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
  },
  emptyText: {
    fontSize: 14,
    color: secondaryTextColor,
  },
  centerContent: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  practiceTitle: {
    marginTop: 24,
  },
  practiceCard: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(88, 86, 214, 0.1)',
  },
  practiceHeader: {
    fontSize: 16,
    fontWeight: '600',
    color: textColor,
    marginBottom: 6,
  },
  practiceContent: {
    fontSize: 14,
    color: secondaryTextColor,
    lineHeight: 20,
  },
});

export default StudySuggestionsScreen;

