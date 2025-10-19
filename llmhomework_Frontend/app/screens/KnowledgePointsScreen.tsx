import { RouteProp, useRoute } from '@react-navigation/native';
import React, { useMemo } from 'react';
import { FlatList, SafeAreaView, StyleSheet, Text, View, ScrollView } from 'react-native';
import { RootStackParamList } from '../navigation/NavigationTypes';
import {
  textPrimary,
  textSecondary,
  backgroundPrimary,
  cardBackground,
  borderColor,
  errorColor,
  errorAlpha10,
  primaryAlpha10
} from '../styles/colors';
import { typography, spacing, borderRadius, shadows } from '../styles/designSystem';

type KnowledgeRouteProp = RouteProp<RootStackParamList, 'KnowledgePoints'>;

const KnowledgePointsScreen: React.FC = () => {
  const route = useRoute<KnowledgeRouteProp>();
  
  // 打印调试信息
  console.log('🔍 KnowledgePointsScreen 接收到的参数:', {
    knowledgePoints: route.params?.knowledgePoints,
    wrongKnowledges: route.params?.wrongKnowledges,
    knowledgeAnalysis: route.params?.knowledgeAnalysis,
    gradingResult: route.params?.gradingResult
  });
  
  const normalizeText = (value: any): string => {
    if (value === null || value === undefined) return '';
    if (typeof value === 'string') return value.trim();
    if (Array.isArray(value)) {
      return value.map((item) => normalizeText(item)).filter(Boolean).join('、');
    }
    if (typeof value === 'object') {
      if (value.content) return normalizeText(value.content);
      if (value.name) return normalizeText(value.name);
      if (value.title) return normalizeText(value.title);
      if (value.text) return normalizeText(value.text);
      return Object.values(value).map((item) => normalizeText(item)).filter(Boolean).join('、');
    }
    return String(value);
  };

  const knowledgePoints = useMemo(() => {
    const raw = route.params?.knowledgePoints ?? [];
    const flattened = Array.isArray(raw) ? raw : [raw];
    const normalized = flattened
      .flatMap((item: any) => {
        if (!item) return [];
        if (Array.isArray(item)) return item;
        const text = normalizeText(item);
        if (!text) return [];
        return text.split(/[,、\s]+/).filter(Boolean);
      })
      .map((text: string) => text.trim())
      .filter((text: string) => text.length > 0);
    return Array.from(new Set(normalized));
  }, [route.params?.knowledgePoints]);

  // 处理错题知识点分析（来自knowledge_analysis）
  const knowledgeAnalysisData = useMemo(() => {
    const analysis = route.params?.knowledgeAnalysis;
    console.log('🔍 处理knowledge_analysis:', analysis);
    
    const wrongKnowledgePoints = analysis?.wrong_knowledge_points || [];
    const studyRecommendations = analysis?.study_recommendations || [];
    
    return {
      wrongKnowledgePoints: Array.isArray(wrongKnowledgePoints) ? wrongKnowledgePoints : [],
      studyRecommendations: Array.isArray(studyRecommendations) ? studyRecommendations : []
    };
  }, [route.params?.knowledgeAnalysis]);

  // 删除学习建议相关逻辑 - 不再需要

  // 计算正确率
  const accuracyData = useMemo(() => {
    const gradingResult = route.params?.gradingResult || [];
    if (!Array.isArray(gradingResult) || gradingResult.length === 0) {
      return { accuracy: 100, totalQuestions: 0, correctQuestions: 0 }; // 默认100%，不显示错题分析
    }
    
    const totalQuestions = gradingResult.length;
    const correctQuestions = gradingResult.filter((result: any) => {
      // 检查多种可能的正确性字段
      return result.correct === true || result.is_correct === true || result.isCorrect === true;
    }).length;
    
    const accuracy = totalQuestions > 0 ? Math.round((correctQuestions / totalQuestions) * 100) : 100;
    
    console.log('📊 正确率计算:', { totalQuestions, correctQuestions, accuracy });
    return { accuracy, totalQuestions, correctQuestions };
  }, [route.params?.gradingResult]);

  const wrongKnowledges = useMemo(() => {
    const raw = route.params?.wrongKnowledges ?? [];
    const arrayRaw = Array.isArray(raw) ? raw : [raw];
    
    // 首先处理传统的wrongKnowledges格式
    const traditionalWrongKnowledges = arrayRaw
      .map((item: any, index: number) => {
        if (!item) return null;
        if (typeof item === 'string') {
          return {
            questionNumber: index + 1,
            title: item,
            description: '该知识点仍需加强训练，以提高正确率。'
          };
        }
        if (typeof item === 'object') {
          const questionNumber = item.questionNumber ?? item.question_number ?? item.index ?? index + 1;
          const title =
            normalizeText(item.knowledge_point) ||
            normalizeText(item.title) ||
            normalizeText(item.name) ||
            normalizeText(item.topic) ||
            '知识点';
          const description =
            normalizeText(item.description) ||
            normalizeText(item.reason) ||
            normalizeText(item.suggestion) ||
            '该知识点仍需加强训练，以提高正确率。';
          return {
            questionNumber,
            title,
            description
          };
        }
        return null;
      })
      .filter(Boolean) as Array<{ questionNumber: number; title: string; description: string }>;
    
    // 然后处理来自knowledge_analysis的错题知识点
    const analysisWrongKnowledges = knowledgeAnalysisData.wrongKnowledgePoints.map((point: string, index: number) => ({
      questionNumber: traditionalWrongKnowledges.length + index + 1,
      title: point,
      description: '该知识点需要重点复习和练习'
    }));
    
    // 合并两种来源的数据
    return [...traditionalWrongKnowledges, ...analysisWrongKnowledges];
  }, [route.params?.wrongKnowledges, knowledgeAnalysisData]);

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={true}
        bounces={true}
      >
        <View style={styles.container}>
          <Text style={styles.sectionTitle}>知识点列表</Text>
          <FlatList
            data={knowledgePoints}
            keyExtractor={(item, index) => `${item}-${index}`}
            renderItem={({ item, index }) => (
              <View style={styles.pointCard}>
                <View style={styles.pointHeader}>
                  <View style={styles.pointIconContainer}>
                    <Text style={styles.pointIcon}>📘</Text>
                  </View>
                  <Text style={styles.pointTitle}>{item || '知识点'}</Text>
                </View>
                <Text style={styles.pointDescription}>该知识点涉及到当前题目，建议继续巩固练习。</Text>
              </View>
            )}
            ListEmptyComponent={
              <View style={styles.emptyCard}>
                <Text style={styles.emptyText}>暂无知识点数据</Text>
              </View>
            }
            contentContainerStyle={knowledgePoints.length ? undefined : styles.flatlistEmpty}
            scrollEnabled={false}
          />

          {/* 错题知识点分析 - 只在正确率<100%时显示 */}
          {accuracyData.accuracy < 100 && (
            <>
              <Text style={[styles.sectionTitle, styles.subTitle]}>错题知识点分析</Text>
              {wrongKnowledges.length > 0 ? (
                wrongKnowledges.map((item: any, index: number) => (
                  <View key={`${item.questionNumber || index}-${item.title}`} style={styles.wrongCard}>
                    <View style={styles.wrongHeader}>
                      <Text style={styles.wrongTitle}>第 {item.questionNumber || index + 1} 题</Text>
                      <Text style={styles.wrongBadge}>需加强</Text>
                    </View>
                    <Text style={styles.wrongPoint}>{item.title || '知识点'}</Text>
                    <Text style={styles.wrongDescription}>
                      {item.description || '该知识点仍需加强训练，以提高正确率。'}
                    </Text>
                  </View>
                ))
              ) : (
                <View style={styles.emptyCard}>
                  <Text style={styles.emptyText}>暂无具体错题知识点分析</Text>
                </View>
              )}
            </>
          )}
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
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
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
  subTitle: {
    marginTop: spacing.xl,
  },
  pointCard: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding,
    marginBottom: spacing.md,
    borderWidth: 0.5,  // Apple 精细边框
    borderColor: borderColor,
    ...shadows.level2,  // 轻柔阴影
  },
  pointHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  pointIconContainer: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: primaryAlpha10,  // 移除紫色调
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  pointIcon: {
    fontSize: 18,
  },
  pointTitle: {
    ...typography.bodyMedium,
    fontWeight: '500',
    color: textPrimary,
  },
  pointDescription: {
    ...typography.bodySmall,
    color: textSecondary,
    lineHeight: 20,
  },
  wrongCard: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding,
    marginBottom: spacing.md,
    borderWidth: 0.5,
    borderColor: errorColor,
  },
  wrongHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  wrongTitle: {
    ...typography.bodyMedium,
    fontWeight: '500',
    color: textPrimary,
  },
  wrongBadge: {
    ...typography.caption,
    color: errorColor,
    backgroundColor: errorAlpha10,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.sm,
  },
  wrongPoint: {
    ...typography.bodyMedium,
    fontWeight: '500',
    color: errorColor,
    marginBottom: spacing.xs,
  },
  wrongDescription: {
    ...typography.bodySmall,
    color: textSecondary,
    lineHeight: 20,
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
  flatlistEmpty: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  subSectionTitle: {
    ...typography.heading4,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.md,
    marginTop: spacing.lg,
  },
  suggestionCard: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding,
    marginBottom: spacing.md,
    borderWidth: 0.5,
    borderColor: borderColor,
    ...shadows.level1,  // 更轻的阴影
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
});

export default KnowledgePointsScreen;

