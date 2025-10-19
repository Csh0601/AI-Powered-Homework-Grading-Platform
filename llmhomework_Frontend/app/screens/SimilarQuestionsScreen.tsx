import { RouteProp, useRoute } from '@react-navigation/native';
import React from 'react';
import { FlatList, SafeAreaView, StyleSheet, Text, View, ScrollView, TouchableOpacity } from 'react-native';
import { RootStackParamList } from '../navigation/NavigationTypes';
import {
  textPrimary,
  textSecondary,
  backgroundPrimary,
  cardBackground,
  borderColor,
  primaryColor,
  primaryAlpha10,
  successColor,
  successAlpha10,
  warningColor,
  warningAlpha10
} from '../styles/colors';
import { typography, spacing, borderRadius, shadows } from '../styles/designSystem';

type SimilarQuestionsRouteProp = RouteProp<RootStackParamList, 'SimilarQuestions'>;

const SimilarQuestionsScreen: React.FC = () => {
  const route = useRoute<SimilarQuestionsRouteProp>();
  const questions = route.params?.questions ?? [];

  const renderQuestionCard = ({ item, index }: { item: any; index: number }) => (
    <View style={styles.questionCard}>
      <View style={styles.cardHeader}>
        <View style={styles.questionNumberContainer}>
          <Text style={styles.questionNumber}>题目 {index + 1}</Text>
        </View>
        <View style={styles.typeContainer}>
          <Text style={styles.typeText}>{item.type || '计算题'}</Text>
        </View>
      </View>
      
      <View style={styles.questionSection}>
        <Text style={styles.sectionTitle}>📝 原题目</Text>
        <Text style={styles.questionText}>{item.originalQuestion}</Text>
      </View>
      
      <View style={styles.divider} />
      
      <View style={styles.questionSection}>
        <Text style={styles.sectionTitle}>🎯 相似题目</Text>
        <Text style={styles.similarQuestionText}>{item.similarQuestion}</Text>
      </View>
      
      <View style={styles.practiceHint}>
        <View style={styles.hintIconContainer}>
          <Text style={styles.hintIcon}>💡</Text>
        </View>
        <Text style={styles.hintText}>建议练习此类似题目，巩固相关知识点</Text>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.gradientBackground} />
      
      <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
        {/* 顶部标题区域 */}
        <View style={styles.header}>
          <View style={styles.headerIconContainer}>
            <Text style={styles.headerIcon}>🎯</Text>
          </View>
          <Text style={styles.headerTitle}>相似的题目</Text>
          <Text style={styles.headerSubtitle}>练习类似题目，提高解题能力</Text>
        </View>

        {/* 相似题目列表 */}
        <View style={styles.questionsSection}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionIcon}>📚</Text>
            <Text style={styles.sectionTitle}>推荐练习题目</Text>
            <Text style={styles.questionCount}>共 {questions.length} 题</Text>
          </View>
          
          {questions.length > 0 ? (
            <FlatList
              data={questions}
              keyExtractor={(item, index) => `${item.questionId}-${index}`}
              renderItem={renderQuestionCard}
              contentContainerStyle={styles.listContent}
              scrollEnabled={false}
              showsVerticalScrollIndicator={false}
            />
          ) : (
            <View style={styles.emptyCard}>
              <View style={styles.emptyIconContainer}>
                <Text style={styles.emptyIcon}>📝</Text>
              </View>
              <Text style={styles.emptyText}>暂无相似题目</Text>
              <Text style={styles.emptySubtext}>当前批改结果中没有生成相似题目</Text>
            </View>
          )}
        </View>

        {/* 学习提示 */}
        <View style={styles.tipsSection}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionIcon}>💡</Text>
            <Text style={styles.sectionTitle}>学习提示</Text>
          </View>
          
          <View style={styles.tipCard}>
            <View style={styles.tipIconContainer}>
              <Text style={styles.tipIcon}>🎯</Text>
            </View>
            <Text style={styles.tipTitle}>如何使用相似题目</Text>
            <Text style={styles.tipContent}>
              1. 先尝试独立解答相似题目{'\n'}
              2. 对比解题思路和步骤{'\n'}
              3. 总结解题方法和技巧{'\n'}
              4. 反复练习类似题型
            </Text>
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
  gradientBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 300,
    backgroundColor: primaryAlpha10,  // 移除紫色调
    borderBottomLeftRadius: 100,
    borderBottomRightRadius: 100,
  },
  container: {
    flex: 1,
    paddingHorizontal: spacing.screenHorizontal,
  },
  header: {
    alignItems: 'center',
    paddingTop: spacing.xl,
    paddingBottom: spacing.xxxl,
  },
  headerIconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: primaryAlpha10,  // 移除紫色调
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.xl,
    borderWidth: 0.5,  // Apple 精细边框
    borderColor: borderColor,
  },
  headerIcon: {
    fontSize: 32,
  },
  headerTitle: {
    ...typography.displayMedium,
    fontWeight: '300',  // Apple 轻量字体
    color: textPrimary,
    marginBottom: spacing.sm,
    textAlign: 'center',
    letterSpacing: -0.5,
  },
  headerSubtitle: {
    ...typography.bodyMedium,
    color: textSecondary,
    textAlign: 'center',
    lineHeight: 22,
    fontWeight: '400',
  },
  questionsSection: {
    marginBottom: spacing.xl,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.xl,
  },
  sectionIcon: {
    fontSize: 20,
    marginRight: spacing.sm,
  },
  sectionTitle: {
    ...typography.heading2,
    fontWeight: '500',  // Apple 中等字重
    color: textPrimary,
    flex: 1,
  },
  questionCount: {
    ...typography.bodySmall,
    color: primaryColor,
    fontWeight: '500',
    backgroundColor: primaryAlpha10,  // 移除紫色调
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.md,
  },
  listContent: {
    gap: spacing.lg,
  },
  questionCard: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding + spacing.sm,
    ...shadows.level2,  // 轻柔阴影
    borderWidth: 0.5,
    borderColor: borderColor,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xl,
  },
  questionNumberContainer: {
    backgroundColor: primaryAlpha10,  // 移除紫色调
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.md,
  },
  questionNumber: {
    ...typography.bodySmall,
    fontWeight: '500',
    color: primaryColor,
  },
  typeContainer: {
    backgroundColor: successAlpha10,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.md,
  },
  typeText: {
    ...typography.caption,
    fontWeight: '500',
    color: successColor,
  },
  questionSection: {
    marginBottom: spacing.lg,
  },
  sectionTitleLocal: {
    ...typography.heading4,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.md,
  },
  questionText: {
    ...typography.bodyMedium,
    color: textPrimary,
    lineHeight: 22,
    fontWeight: '400',
    backgroundColor: primaryAlpha10,
    padding: spacing.lg,
    borderRadius: borderRadius.md,
    borderLeftWidth: 3,
    borderLeftColor: primaryColor,
  },
  divider: {
    height: 0.5,  // Apple 精细分割线
    backgroundColor: borderColor,
    marginVertical: spacing.lg,
  },
  similarQuestionText: {
    ...typography.bodyMedium,
    color: textPrimary,
    lineHeight: 22,
    fontWeight: '400',
    backgroundColor: warningAlpha10,
    padding: spacing.lg,
    borderRadius: borderRadius.md,
    borderLeftWidth: 3,
    borderLeftColor: warningColor,
  },
  practiceHint: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: successAlpha10,
    padding: spacing.lg,
    borderRadius: borderRadius.md,
    marginTop: spacing.sm,
  },
  hintIconContainer: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: successAlpha10,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  hintIcon: {
    fontSize: 16,
  },
  hintText: {
    ...typography.bodySmall,
    color: successColor,
    fontWeight: '500',
    flex: 1,
  },
  emptyCard: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.xxxl + spacing.sm,
    alignItems: 'center',
    ...shadows.level2,  // 轻柔阴影
  },
  emptyIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: primaryAlpha10,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.lg,
  },
  emptyIcon: {
    fontSize: 32,
  },
  emptyText: {
    ...typography.heading3,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  emptySubtext: {
    ...typography.bodySmall,
    color: textSecondary,
    textAlign: 'center',
    lineHeight: 20,
  },
  tipsSection: {
    marginBottom: spacing.xxxl + spacing.md,
  },
  tipCard: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding + spacing.sm,
    ...shadows.level2,  // 轻柔阴影
    borderWidth: 0.5,
    borderColor: borderColor,
  },
  tipIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: warningAlpha10,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.lg,
    alignSelf: 'center',
  },
  tipIcon: {
    fontSize: 24,
  },
  tipTitle: {
    ...typography.heading3,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.md,
    textAlign: 'center',
  },
  tipContent: {
    ...typography.bodyMedium,
    color: textSecondary,
    lineHeight: 22,
    fontWeight: '400',
  },
});

export default SimilarQuestionsScreen;
