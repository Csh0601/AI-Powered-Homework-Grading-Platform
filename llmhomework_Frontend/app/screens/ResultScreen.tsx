import { RouteProp, useRoute, useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useEffect, useMemo, useState } from 'react';
import { FlatList, StyleSheet, Text, View, ScrollView, SafeAreaView, Animated, Dimensions, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import ResultItem from '../components/ResultItem';
import { CapsuleButton } from '../components/shared/CapsuleButton';
import { Card } from '../components/shared/Card';
import { StatCard } from '../components/shared/StatCard';
import { Button } from '../components/shared/Button';
import { CorrectionResult } from '../models/CorrectionResult';
import { RootStackParamList } from '../navigation/NavigationTypes';
import {
  primaryColor,
  successColor,
  errorColor,
  textPrimary,
  textSecondary,
  backgroundPrimary,
  cardBackground,
  primaryAlpha10,
  successAlpha10,
  errorAlpha10
} from '../styles/colors';
import { typography, spacing, borderRadius, shadows } from '../styles/designSystem';

const { width: screenWidth } = Dimensions.get('window');

// 路由类型
type ResultScreenRouteProp = RouteProp<RootStackParamList, 'Result'>;

const ResultScreen: React.FC = () => {
  const route = useRoute<ResultScreenRouteProp>();
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  
  // 调试：打印接收到的所有参数
  console.log('\n=== 🔍 ResultScreen 数据流分析 ===');
  console.log('🔍 完整route.params:', JSON.stringify(route.params, null, 2));
  
  const resultId = route.params?.resultId;
  const gradingResult = route.params?.gradingResult as any;
  
  console.log('🔍 gradingResult类型:', typeof gradingResult);
  console.log('🔍 gradingResult是否存在:', !!gradingResult);
  if (gradingResult) {
    console.log('🔍 gradingResult顶层字段:', Object.keys(gradingResult));
    console.log('🔍 grading_result字段:', gradingResult.grading_result);
    console.log('🔍 questions字段:', gradingResult.questions);
  }
  const wrongKnowledgesParam = route.params?.wrongKnowledges || [];
  const history = route.params?.history || [];
  const taskId = route.params?.taskId || gradingResult?.task_id || '未知任务';
  const rawTimestamp = route.params?.timestamp ?? gradingResult?.timestamp ?? Date.now();

  // 改进的文本提取函数
  const safeText = (value: any, fallback: string = '', debugContext?: string): string => {
    if (typeof value === 'string' && value.trim()) {
      return value.trim();
    }
    if (typeof value === 'number') {
      return String(value);
    }
    if (Array.isArray(value)) {
      const joined = value.filter(Boolean).join('\n');
      return joined || fallback;
    }
    if (value && typeof value === 'object') {
      const joined = Object.values(value).filter(Boolean).join(' ');
      return joined || fallback;
    }
    
    // 只在使用fallback且是关键字段时才打印调试信息
    if (debugContext === 'question' && !value) {
      console.log(`🚨 ${debugContext}字段为空，使用fallback:`, { value, fallback });
    }
    return fallback;
  };

  // 简化的时间格式化
  const formatSubmissionTime = (input: number | string) => {
    if (!input) return '未知时间';
    
    let date: Date;
    if (typeof input === 'string') {
      date = new Date(input);
    } else {
      date = new Date(input > 9999999999 ? input : input * 1000);
    }
    
    if (isNaN(date.getTime())) return '未知时间';
    
    return new Intl.DateTimeFormat('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    }).format(date);
  };

  // 直接从后端数据构建题目列表
  const processedData = useMemo(() => {
    console.log('🔍 开始处理数据，gradingResult:', gradingResult);
    
    if (!gradingResult) {
      return {
        questions: [],
        summary: { totalScore: 0, correctCount: 0, totalQuestions: 0, accuracy: 0, knowledgePoints: [] },
        wrongKnowledges: [],
        similarQuestions: [],
        timestamp: rawTimestamp
      };
    }

    // 直接使用 grading_result 数组，这是最完整的数据
    const sourceQuestions = gradingResult.grading_result || gradingResult.questions || [];
    console.log('🔍 源题目数据:', sourceQuestions);

    // 先过滤和去重源数据，避免重复题目
    const uniqueSourceQuestions = sourceQuestions.filter((item: any, index: number, arr: any[]) => {
      const questionId = item.question_id || item.id || `q_${String(index + 1).padStart(3, '0')}`;
      // 检查是否是第一次出现这个questionId
      return arr.findIndex((q: any) => (q.question_id || q.id || `q_${String(arr.indexOf(q) + 1).padStart(3, '0')}`) === questionId) === index;
    });
    
    console.log('🔍 源题目数量:', sourceQuestions.length);
    console.log('🔍 去重后题目数量:', uniqueSourceQuestions.length);
    if (sourceQuestions.length !== uniqueSourceQuestions.length) {
      console.warn('⚠️ 发现重复题目，已自动去重');
    }

    const normalizedQuestions: CorrectionResult[] = uniqueSourceQuestions.map((item: any, index: number) => {
      console.log(`🔍 处理题目 ${index + 1}:`, item);
      console.log(`🔍 原始数据字段:`, Object.keys(item));
      console.log(`🔍 题目内容字段值:`, {
        question: item.question,
        question_text: item.question_text,
        stem: item.stem,
        content: item.content,
        problem: item.problem,
        title: item.title
      });
      
      // 直接提取字段，不做复杂转换 - 扩展更多可能的字段名
      const questionText = safeText(
        item.question || item.question_text || item.stem || item.content || item.problem || item.title, 
        `题目 ${index + 1}`,
        'question'  // 只对题目内容进行特殊调试
      );
      
      // 额外的安全检查：如果题目内容仍然是fallback，记录警告
      if (questionText === `题目 ${index + 1}`) {
        console.warn(`⚠️ 题目 ${index + 1} 所有内容字段都为空:`, {
          原始数据: item,
          检查字段: {
            question: item.question,
            question_text: item.question_text,
            stem: item.stem,
            content: item.content,
            problem: item.problem,
            title: item.title
          }
        });
      }
      const userAnswerText = safeText(item.answer || item.user_answer || item.student_answer, '未作答');
      const correctAnswerText = safeText(item.correct_answer || item.standard_answer, '参考答案');
      const explanationText = safeText(item.explanation || item.analysis || item.feedback, '暂无详细解析');
      
      // 处理知识点
      let knowledgePoints: string[] = [];
      if (Array.isArray(item.knowledge_points)) {
        knowledgePoints = item.knowledge_points.filter(Boolean);
      } else if (typeof item.knowledge_point === 'string') {
        knowledgePoints = [item.knowledge_point];
      }
      
      const result: CorrectionResult = {
        questionId: item.question_id || item.id || `q_${String(index + 1).padStart(3, '0')}`,
        question: questionText,
        userAnswer: userAnswerText,
        correctAnswer: correctAnswerText,
        isCorrect: Boolean(item.correct || item.is_correct),
        explanation: explanationText,
        score: Number(item.score) || 0,
        type: item.type || '计算题',
        knowledgePoint: knowledgePoints.join('、') || '基础知识点',
        knowledgePoints,
        questionIndex: index
      };

      console.log(`🔍 处理完成题目 ${index + 1}:`, {
        questionId: result.questionId,
        question: result.question.substring(0, 50) + '...',
        questionFull: result.question,  // 显示完整题目内容
        userAnswer: result.userAnswer.substring(0, 50) + '...',
        correctAnswer: result.correctAnswer,
        explanation: (result.explanation || '').substring(0, 50) + '...'
      });

      return result;
    });

    // 处理统计信息
    const summary = gradingResult.summary || {};
    const normalizedSummary = {
      totalScore: Number(summary.total_score) || normalizedQuestions.reduce((sum, q) => sum + (q.score || 0), 0),
      correctCount: Number(summary.correct_count) || normalizedQuestions.filter(q => q.isCorrect).length,
      totalQuestions: Number(summary.total_questions) || normalizedQuestions.length,
      accuracy: Number(summary.accuracy_rate) || (normalizedQuestions.length > 0 ? normalizedQuestions.filter(q => q.isCorrect).length / normalizedQuestions.length : 0),
      knowledgePoints: Array.isArray(summary.knowledge_points) ? summary.knowledge_points : []
    };

    // 处理错题知识点
    const wrongKnowledgesList = wrongKnowledgesParam.length > 0 
      ? wrongKnowledgesParam 
      : gradingResult.wrong_knowledges || [];
    
    const normalizedWrongKnowledges = Array.isArray(wrongKnowledgesList) 
      ? wrongKnowledgesList.map((item: any, index: number) => ({
          questionNumber: index + 1,
          title: typeof item === 'string' ? item : (item.title || item.knowledge_point || '知识点'),
          description: typeof item === 'object' ? (item.description || '该知识点需要加强练习') : '该知识点需要加强练习'
        }))
      : [];

    // 收集相似题目
    const similarQuestions: Array<{
      questionId: string;
      originalQuestion: string;
      similarQuestion: string;
      type?: string;
    }> = [];

    // 从grading_result中收集相似题目
    normalizedQuestions.forEach((question, index) => {
      const originalItem = sourceQuestions[index] || {};
      const similarQuestion = originalItem.similar_question;
      
      if (similarQuestion && typeof similarQuestion === 'string' && similarQuestion.trim()) {
        similarQuestions.push({
          questionId: question.questionId,
          originalQuestion: question.question,
          similarQuestion: similarQuestion.trim(),
          type: question.type
        });
      }
    });

    // 如果有summary级别的相似题目，也添加进去
    if (gradingResult.summary?.similar_question && typeof gradingResult.summary.similar_question === 'string') {
      const summaryQuestion = gradingResult.summary.similar_question.trim();
      if (summaryQuestion && !similarQuestions.some(q => q.similarQuestion === summaryQuestion)) {
        similarQuestions.push({
          questionId: 'summary',
          originalQuestion: '整体练习',
          similarQuestion: summaryQuestion,
          type: '综合练习'
        });
      }
    }

    console.log('🔍 最终处理结果:', {
      questionsCount: normalizedQuestions.length,
      summary: normalizedSummary,
      wrongKnowledgesCount: normalizedWrongKnowledges.length,
      similarQuestionsCount: similarQuestions.length
    });

    return {
      questions: normalizedQuestions,
      summary: normalizedSummary,
      wrongKnowledges: normalizedWrongKnowledges,
      similarQuestions: similarQuestions,
      timestamp: rawTimestamp
    };
  }, [gradingResult, rawTimestamp, wrongKnowledgesParam]);

  const submissionTime = formatSubmissionTime(processedData.timestamp);

  // 如果没有gradingResult但有resultId，尝试从历史记录加载
  useEffect(() => {
    if (!gradingResult && resultId) {
      // TODO: 这里应该从历史记录服务加载数据
      // 暂时静默处理，避免控制台输出
    }
  }, [resultId, gradingResult]);

  // 验证数据完整性
  if (!gradingResult && !resultId) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.container}>
          <View style={styles.noDataCard}>
            <View style={styles.noDataIconContainer}>
              <Ionicons name="alert-circle-outline" size={32} color={primaryColor} />
            </View>
            <Text style={styles.noDataText}>数据加载失败</Text>
            <Text style={styles.noDataSubtext}>请重新上传图片进行批改</Text>
          </View>
        </View>
      </SafeAreaView>
    );
  }

  const [fadeAnim] = useState(new Animated.Value(0));
  const [slideAnim] = useState(new Animated.Value(50));
  const [scaleAnim] = useState(new Animated.Value(0.95));

  useEffect(() => {
    // 启动动画
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.spring(slideAnim, {
        toValue: 0,
        tension: 50,
        friction: 7,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 60,
        friction: 8,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  // 计算统计数据
  const actualCorrectCount = processedData.summary.correctCount;
  const actualAccuracy = Math.min(processedData.summary.accuracy * 100, 100);

  // 如果没有题目数据，显示提示信息
  if (processedData.questions.length === 0) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
          <View style={styles.header}>
            <View style={styles.headerIconContainer}>
              <Ionicons name="stats-chart-outline" size={32} color={primaryColor} />
            </View>
            <Text style={styles.headerTitle}>批改结果</Text>
            <Text style={styles.headerSubtitle}>暂无批改数据</Text>
          </View>

          <View style={styles.noDataCard}>
            <View style={styles.noDataIconContainer}>
              <Ionicons name="document-text-outline" size={32} color={primaryColor} />
            </View>
            <Text style={styles.noDataText}>暂无批改结果</Text>
            <Text style={styles.noDataSubtext}>请先上传作业图片进行批改</Text>
          </View>
        </ScrollView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
        <Animated.View 
          style={{
            opacity: fadeAnim,
            transform: [
              { translateY: slideAnim },
              { scale: scaleAnim }
            ]
          }}
        >
          {/* 顶部标题区域 - Apple 简洁风格 */}
          <View style={styles.header}>
            <View style={styles.headerIconContainer}>
              <Ionicons name="stats-chart-outline" size={32} color={primaryColor} />
            </View>
            <Text style={styles.headerTitle}>批改结果</Text>
            <Text style={styles.headerSubtitle}>查看详细批改情况</Text>
          </View>

          {/* 任务信息卡片 */}
          <View style={styles.taskInfoCard}>
            <View style={styles.cardHeader}>
              <View style={styles.cardHeaderLeft}>
                <Ionicons name="clipboard-outline" size={20} color={textPrimary} />
                <Text style={styles.cardHeaderTitle}>任务信息</Text>
              </View>
              <View style={styles.taskStatusBadge}>
                <Ionicons name="checkmark-circle" size={14} color={successColor} style={{ marginRight: 4 }} />
                <Text style={styles.taskStatusText}>已完成</Text>
              </View>
            </View>
            <View style={styles.taskInfoContent}>
              <View style={styles.taskInfoRow}>
                <View style={styles.taskInfoLabelContainer}>
                  <Ionicons name="time-outline" size={14} color={textSecondary} style={{ marginRight: 4 }} />
                  <Text style={styles.taskInfoLabel}>提交时间</Text>
                </View>
                <Text style={styles.taskInfoValue}>{submissionTime}</Text>
              </View>
              <View style={styles.taskInfoRow}>
                <View style={styles.taskInfoLabelContainer}>
                  <Ionicons name="card-outline" size={14} color={textSecondary} style={{ marginRight: 4 }} />
                  <Text style={styles.taskInfoLabel}>任务编号</Text>
                </View>
                <Text style={styles.taskInfoValue}>{taskId.substring(0, 8)}...</Text>
              </View>
            </View>
          </View>
          
          {/* 总体统计 */}
          <View style={styles.statsContainer}>
            <View style={styles.sectionHeader}>
              <Ionicons name="trending-up-outline" size={20} color={primaryColor} style={{ marginRight: 8 }} />
              <Text style={styles.sectionTitle}>总体统计</Text>
            </View>
            <View style={styles.statsGridSimplified}>
              <View style={[styles.statCard, styles.correctCard]}>
                <View style={styles.statIconContainer}>
                  <Ionicons name="checkmark-circle-outline" size={24} color={successColor} />
                </View>
                <Text style={[styles.statValue, styles.correctText]}>
                  {actualCorrectCount}/{processedData.summary.totalQuestions}
                </Text>
                <Text style={styles.statLabel}>正确</Text>
              </View>
              <View style={[styles.statCard, styles.accuracyCard]}>
                <View style={styles.statIconContainer}>
                  <Ionicons name="stats-chart-outline" size={24} color={primaryColor} />
                </View>
                <Text style={styles.statValue}>{actualAccuracy.toFixed(1)}%</Text>
                <Text style={styles.statLabel}>正确率</Text>
              </View>
            </View>
          </View>

          {/* 题目详情 */}
          <View style={styles.questionsSection}>
            <View style={styles.sectionHeader}>
              <Ionicons name="document-text-outline" size={20} color={primaryColor} style={{ marginRight: 8 }} />
              <Text style={styles.sectionTitle}>题目详情</Text>
            </View>
            {processedData.questions.length > 0 ? (
              <FlatList
                data={processedData.questions}
                keyExtractor={(item, index) => `question-${taskId}-${index}-${item.questionId || 'unknown'}`}
                renderItem={({ item }) => (
                  <ResultItem 
                    result={item as CorrectionResult}
                    onPressExplanation={() => navigation.navigate('Explanation', { result: item })}
                    onPressKnowledge={() => navigation.navigate('KnowledgePoints', { 
                      knowledgePoints: item.knowledgePoints || [item.knowledgePoint],
                      wrongKnowledges: processedData.wrongKnowledges,
                      knowledgeAnalysis: gradingResult?.knowledge_analysis,
                      gradingResult: gradingResult?.grading_result || []
                    })}
                  />
                )}
                contentContainerStyle={styles.listContent}
                scrollEnabled={false}
              />
            ) : (
              <View style={styles.noDataCard}>
                <View style={styles.noDataIconContainer}>
                  <Ionicons name="document-text-outline" size={32} color={primaryColor} />
                </View>
                <Text style={styles.noDataText}>暂无批改结果</Text>
                <Text style={styles.noDataSubtext}>请先上传作业图片进行批改</Text>
              </View>
            )}
          </View>

          {/* 知识点分析 */}
          <View style={styles.simpleSection}>
            <View style={styles.sectionHeader}>
              <View style={styles.sectionTitleContainer}>
                <Ionicons name="bulb-outline" size={20} color={primaryColor} style={{ marginRight: 8 }} />
                <Text style={styles.sectionTitle}>知识点分析</Text>
              </View>
              <CapsuleButton
                title="查看详情"
                iconName="arrow-forward"
                onPress={() => navigation.navigate('KnowledgePoints', {
                  knowledgePoints: processedData.summary.knowledgePoints || [],
                  wrongKnowledges: processedData.wrongKnowledges,
                  knowledgeAnalysis: gradingResult?.knowledge_analysis,
                  gradingResult: gradingResult?.grading_result || []
                })}
                variant="outline"
              />
            </View>
            <Text style={styles.simpleSectionHint}>点击查看详细知识点分析</Text>
          </View>

          {/* 学习建议 */}
          <View style={styles.simpleSection}>
            <View style={styles.sectionHeader}>
              <View style={styles.sectionTitleContainer}>
                <Ionicons name="bulb-outline" size={20} color={primaryColor} style={{ marginRight: 8 }} />
                <Text style={styles.sectionTitle}>学习建议</Text>
              </View>
              <CapsuleButton
                title="查看详情"
                iconName="arrow-forward"
                onPress={() => navigation.navigate('StudySuggestions', {
                  suggestions: gradingResult?.knowledge_analysis?.study_recommendations || [],
                  practiceQuestions: gradingResult?.practice_questions || [],
                  learningSuggestions: processedData.questions.flatMap(q => (q as any).learning_suggestions || []),
                  summaryLearningSuggestions: gradingResult?.summary?.learning_suggestions || []
                })}
                variant="outline"
              />
            </View>
            <Text style={styles.simpleSectionHint}>点击查看详细学习建议</Text>
          </View>

          {/* 相似的题目 */}
          <View style={styles.simpleSection}>
            <View style={styles.sectionHeader}>
              <View style={styles.sectionTitleContainer}>
                <Ionicons name="copy-outline" size={20} color={primaryColor} style={{ marginRight: 8 }} />
                <Text style={styles.sectionTitle}>相似题目</Text>
              </View>
              <CapsuleButton
                title="查看详情"
                iconName="arrow-forward"
                onPress={() => navigation.navigate('SimilarQuestions', {
                  questions: processedData.similarQuestions
                })}
                variant="outline"
              />
            </View>
            <Text style={styles.simpleSectionHint}>点击查看更多练习题目</Text>
          </View>

          {/* AI学习伙伴对话入口 */}
          <TouchableOpacity
            style={styles.aiChatSection}
            onPress={() => navigation.navigate('Chat', {
              taskId: String(processedData.timestamp || Date.now()),
              gradingResult: gradingResult
            })}
            activeOpacity={0.8}
          >
            <View style={styles.aiChatHeader}>
              <View style={styles.aiChatIconContainer}>
                <Ionicons name="chatbubble-ellipses-outline" size={28} color={primaryColor} />
              </View>
              <View style={styles.aiChatTextContainer}>
                <Text style={styles.aiChatTitle}>AI 学习伙伴</Text>
                <Text style={styles.aiChatSubtitle}>
                  针对批改结果，AI 可以解答你的疑问
                </Text>
              </View>
              <View style={styles.aiChatArrowContainer}>
                <Ionicons name="chevron-forward" size={24} color={primaryColor} />
              </View>
            </View>
          </TouchableOpacity>
        </Animated.View>
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
    paddingHorizontal: spacing.screenHorizontal,
  },
  header: {
    alignItems: 'center',
    paddingTop: spacing.xl,
    paddingBottom: spacing.xxl,
  },
  headerIconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: primaryAlpha10,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.lg,
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
  },
  headerSubtitle: {
    ...typography.bodyMedium,
    color: textSecondary,
    textAlign: 'center',
    fontWeight: '400',
  },
  taskInfoCard: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding,
    marginBottom: spacing.xl,
    ...shadows.level2,  // 轻柔阴影
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  cardHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  cardHeaderIcon: {
    fontSize: 20,
  },
  cardHeaderTitle: {
    ...typography.heading3,
    fontWeight: '500',  // Apple 中等字重
    color: textPrimary,
  },
  taskInfoLabelContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  taskStatusBadge: {
    backgroundColor: successAlpha10,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.button,
    flexDirection: 'row',
    alignItems: 'center',
  },
  taskStatusText: {
    color: successColor,
    ...typography.label,
    fontWeight: '500',
  },
  taskInfoContent: {
    gap: spacing.md,
  },
  taskInfoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.md,
    backgroundColor: primaryAlpha10,
    borderRadius: borderRadius.md,
  },
  taskInfoLabel: {
    ...typography.bodySmall,
    color: textSecondary,
    fontWeight: '500',
  },
  taskInfoValue: {
    ...typography.bodySmall,
    color: textPrimary,
    fontWeight: '500',
  },
  statsContainer: {
    marginBottom: spacing.xl,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.lg,
  },
  sectionTitleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  sectionIcon: {
    fontSize: 20,
  },
  sectionTitle: {
    ...typography.heading2,
    fontWeight: '500',  // Apple 中等字重
    color: textPrimary,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  statsGridSimplified: {
    flexDirection: 'row',
    gap: spacing.md,
    justifyContent: 'space-between',
  },
  statCard: {
    flex: 1,
    minWidth: (screenWidth - spacing.screenHorizontal * 2 - spacing.md) / 2,
    backgroundColor: cardBackground,
    padding: spacing.lg,
    borderRadius: borderRadius.card,
    alignItems: 'center',
    ...shadows.level2,  // 轻柔阴影
  },
  statIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: primaryAlpha10,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
  },
  statIcon: {
    fontSize: 24,
  },
  statValue: {
    ...typography.displaySmall,
    fontWeight: '300',  // Apple 轻量字体
    color: textPrimary,
    marginBottom: spacing.xs,
  },
  statLabel: {
    ...typography.caption,
    color: textSecondary,
    fontWeight: '500',
  },
  correctCard: {
    backgroundColor: successAlpha10,
  },
  correctText: {
    color: successColor,
  },
  accuracyCard: {
    backgroundColor: primaryAlpha10,
  },
  questionsSection: {
    marginBottom: spacing.xl,
  },
  listContent: {
    paddingBottom: spacing.sm,
    gap: spacing.md,
  },
  noDataCard: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.xxxl,
    alignItems: 'center',
    ...shadows.level2,
  },
  noDataIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: primaryAlpha10,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
  },
  noDataIcon: {
    fontSize: 28,
  },
  noDataText: {
    ...typography.heading4,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  noDataSubtext: {
    ...typography.bodySmall,
    color: textSecondary,
    textAlign: 'center',
  },
  knowledgeSection: {
    marginBottom: spacing.xl,
  },
  simpleSection: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding,
    marginBottom: spacing.xl,
    ...shadows.level1,  // 更轻的阴影
  },
  simpleSectionHint: {
    ...typography.bodyMedium,
    color: textSecondary,
    textAlign: 'center',
    marginTop: spacing.sm,
  },
  knowledgeCard: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding,
    marginBottom: spacing.md,
    ...shadows.level2,
  },
  knowledgeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  knowledgeNumberContainer: {
    backgroundColor: errorAlpha10,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.md,
  },
  knowledgeNumber: {
    ...typography.caption,
    fontWeight: '500',
    color: errorColor,
  },
  knowledgeTitle: {
    ...typography.heading4,
    fontWeight: '500',
    color: textPrimary,
  },
  knowledgeDescription: {
    ...typography.bodySmall,
    color: textSecondary,
  },
  noKnowledgeCard: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.xxxl,
    alignItems: 'center',
    ...shadows.level2,
  },
  noKnowledgeIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: successAlpha10,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
  },
  noKnowledgeIcon: {
    fontSize: 28,
  },
  noKnowledgeText: {
    ...typography.heading4,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  noKnowledgeSubtext: {
    ...typography.bodySmall,
    color: textSecondary,
    textAlign: 'center',
  },
  suggestionsSection: {
    marginBottom: spacing.xxxl,
  },
  suggestionsCard: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.xl,
    ...shadows.level2,
  },
  suggestionsIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: primaryAlpha10,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
    alignSelf: 'center',
  },
  suggestionsIcon: {
    fontSize: 24,
  },
  suggestionsTitle: {
    ...typography.heading3,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.md,
    textAlign: 'center',
  },
  suggestionsContent: {
    ...typography.bodyMedium,
    color: textSecondary,
    textAlign: 'center',
    fontWeight: '400',
  },
  viewMoreText: {
    ...typography.bodySmall,
    color: primaryColor,
    fontWeight: '500',
  },
  similarQuestionsSection: {
    marginBottom: spacing.xxxl,
  },
  similarQuestionsCard: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.xl,
    ...shadows.level2,
  },
  similarQuestionsIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: primaryAlpha10,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
    alignSelf: 'center',
  },
  similarQuestionsIcon: {
    fontSize: 24,
  },
  similarQuestionsTitle: {
    ...typography.heading3,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.md,
    textAlign: 'center',
  },
  similarQuestionsContent: {
    ...typography.bodyMedium,
    color: textSecondary,
    textAlign: 'center',
    fontWeight: '400',
    marginBottom: spacing.md,
  },
  similarQuestionsPreview: {
    gap: spacing.md,
  },
  previewQuestionCard: {
    backgroundColor: primaryAlpha10,
    padding: spacing.md,
    borderRadius: borderRadius.md,
  },
  previewQuestionNumber: {
    ...typography.caption,
    fontWeight: '500',
    color: primaryColor,
    marginBottom: spacing.xs,
  },
  previewQuestionText: {
    ...typography.bodySmall,
    color: textPrimary,
    fontWeight: '400',
  },
  noSimilarQuestionsCard: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.xxxl,
    alignItems: 'center',
    ...shadows.level2,
  },
  // AI学习伙伴对话入口 - Apple 简洁风格
  aiChatSection: {
    marginTop: spacing.lg,
    marginBottom: spacing.lg,
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding,
    ...shadows.level2,
  },
  aiChatHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  aiChatIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: primaryAlpha10,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  aiChatIcon: {
    fontSize: 24,
  },
  aiChatTextContainer: {
    flex: 1,
  },
  aiChatTitle: {
    ...typography.heading4,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.xs / 2,
  },
  aiChatSubtitle: {
    ...typography.caption,
    color: textSecondary,
  },
  aiChatArrowContainer: {
    marginLeft: spacing.sm,
  },
  aiChatArrow: {
    fontSize: 24,
    color: primaryColor,
    fontWeight: '300',
  },
  noSimilarQuestionsIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: primaryAlpha10,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
  },
  noSimilarQuestionsIcon: {
    fontSize: 28,
  },
  noSimilarQuestionsText: {
    ...typography.heading4,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  noSimilarQuestionsSubtext: {
    ...typography.bodySmall,
    color: textSecondary,
    textAlign: 'center',
  },
});

export default ResultScreen;