import { RouteProp, useRoute, useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useEffect, useMemo, useState } from 'react';
import { FlatList, StyleSheet, Text, View, ScrollView, SafeAreaView, Animated, Dimensions, TouchableOpacity } from 'react-native';
import ResultItem from '../components/ResultItem';
import { DecorativeButton } from '../components/DecorativeButton';
import { CorrectionResult } from '../models/CorrectionResult';
import { RootStackParamList } from '../navigation/NavigationTypes';
import { 
  primaryColor, 
  successColor, 
  errorColor,
  textColor, 
  secondaryTextColor, 
  backgroundColor, 
  cardBackgroundColor,
  borderColor,
  systemGray6,
  secondaryColor,
  warningColor
} from '../styles/colors';

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
              <Text style={styles.noDataIcon}>⚠️</Text>
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
        <View style={styles.gradientBackground} />
        <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
          <View style={styles.header}>
            <View style={styles.headerIconContainer}>
              <Text style={styles.headerIcon}>📊</Text>
            </View>
            <Text style={styles.headerTitle}>批改结果</Text>
            <Text style={styles.headerSubtitle}>暂无批改数据</Text>
          </View>
          
          <View style={styles.noDataCard}>
            <View style={styles.noDataIconContainer}>
              <Text style={styles.noDataIcon}>📝</Text>
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
      {/* 渐变背景装饰 */}
      <View style={styles.gradientBackground} />
      
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
          {/* 顶部标题区域 */}
          <View style={styles.header}>
            <View style={styles.headerIconContainer}>
              <Text style={styles.headerIcon}>📊</Text>
            </View>
            <Text style={styles.headerTitle}>批改结果</Text>
            <Text style={styles.headerSubtitle}>查看详细的作业批改情况</Text>
          </View>
          
          {/* 任务信息卡片 */}
          <View style={styles.taskInfoCard}>
            <View style={styles.cardHeader}>
              <View style={styles.cardHeaderLeft}>
                <Text style={styles.cardHeaderIcon}>📋</Text>
                <Text style={styles.cardHeaderTitle}>任务信息</Text>
              </View>
              <View style={styles.taskStatusBadge}>
                <Text style={styles.taskStatusText}>✓ 已完成</Text>
              </View>
            </View>
            <View style={styles.taskInfoContent}>
              <View style={styles.taskInfoRow}>
                <Text style={styles.taskInfoLabel}>📝 提交时间</Text>
                <Text style={styles.taskInfoValue}>{submissionTime}</Text>
              </View>
              <View style={styles.taskInfoRow}>
                <Text style={styles.taskInfoLabel}>🆔 任务编号</Text>
                <Text style={styles.taskInfoValue}>{taskId.substring(0, 8)}...</Text>
              </View>
            </View>
          </View>
          
          {/* 总体统计 */}
          <View style={styles.statsContainer}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionIcon}>📈</Text>
              <Text style={styles.sectionTitle}>总体统计</Text>
            </View>
            <View style={styles.statsGridSimplified}>
              <View style={[styles.statCard, styles.correctCard]}>
                <View style={styles.statIconContainer}>
                  <Text style={styles.statIcon}>✅</Text>
                </View>
                <Text style={[styles.statValue, styles.correctText]}>
                  {actualCorrectCount}/{processedData.summary.totalQuestions}
                </Text>
                <Text style={styles.statLabel}>正确</Text>
              </View>
              <View style={[styles.statCard, styles.accuracyCard]}>
                <View style={styles.statIconContainer}>
                  <Text style={styles.statIcon}>📊</Text>
                </View>
                <Text style={styles.statValue}>{actualAccuracy.toFixed(1)}%</Text>
                <Text style={styles.statLabel}>正确率</Text>
              </View>
            </View>
          </View>

          {/* 题目详情 */}
          <View style={styles.questionsSection}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionIcon}>📝</Text>
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
                  <Text style={styles.noDataIcon}>📝</Text>
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
                <Text style={styles.sectionIcon}>🧠</Text>
                <Text style={styles.sectionTitle}>知识点分析</Text>
              </View>
              <DecorativeButton
                onPress={() => navigation.navigate('KnowledgePoints', { 
                  knowledgePoints: processedData.summary.knowledgePoints || [],
                  wrongKnowledges: processedData.wrongKnowledges,
                  knowledgeAnalysis: gradingResult?.knowledge_analysis,
                  gradingResult: gradingResult?.grading_result || []
                })}
                iconName="book"
                size="sm"
                gradientColors={['#FF6B35', '#F7931E']}
                outerColor="#FFD60A"
                borderColor="#FF8C00"
              />
            </View>
            <Text style={styles.simpleSectionHint}>点击按钮查看详细知识点分析</Text>
          </View>

          {/* 学习建议 */}
          <View style={styles.simpleSection}>
            <View style={styles.sectionHeader}>
              <View style={styles.sectionTitleContainer}>
                <Text style={styles.sectionIcon}>💡</Text>
                <Text style={styles.sectionTitle}>学习建议</Text>
              </View>
              <DecorativeButton
                onPress={() => navigation.navigate('StudySuggestions', { 
                  suggestions: gradingResult?.knowledge_analysis?.study_recommendations || [],
                  practiceQuestions: gradingResult?.practice_questions || [],
                  learningSuggestions: processedData.questions.flatMap(q => (q as any).learning_suggestions || []),
                  summaryLearningSuggestions: gradingResult?.summary?.learning_suggestions || []
                })}
                iconName="bulb"
                size="sm"
                gradientColors={['#32D74B', '#30D158']}
                outerColor="#A3F3BE"
                borderColor="#00C851"
              />
            </View>
            <Text style={styles.simpleSectionHint}>点击按钮查看详细学习建议</Text>
          </View>

          {/* 相似的题目 */}
          <View style={styles.simpleSection}>
            <View style={styles.sectionHeader}>
              <View style={styles.sectionTitleContainer}>
                <Text style={styles.sectionIcon}>🎯</Text>
                <Text style={styles.sectionTitle}>相似的题目</Text>
              </View>
              <DecorativeButton
                onPress={() => navigation.navigate('SimilarQuestions', { 
                  questions: processedData.similarQuestions 
                })}
                iconName="copy"
                size="sm"
                gradientColors={['#5856D6', '#AF52DE']}
                outerColor="#BF5AF2"
                borderColor="#8E44AD"
              />
            </View>
            <Text style={styles.simpleSectionHint}>点击按钮查看详细相似题目</Text>
          </View>
        </Animated.View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: backgroundColor,
  },
  gradientBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 300,
    backgroundColor: 'rgba(88, 86, 214, 0.04)',
    borderBottomLeftRadius: 100,
    borderBottomRightRadius: 100,
  },
  container: {
    flex: 1,
    paddingHorizontal: 20,
  },
  header: {
    alignItems: 'center',
    paddingTop: 20,
    paddingBottom: 32,
  },
  headerIconContainer: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: 'rgba(88, 86, 214, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
    borderWidth: 2,
    borderColor: 'rgba(88, 86, 214, 0.2)',
  },
  headerIcon: {
    fontSize: 32,
  },
  headerTitle: {
    fontSize: 32,
    fontWeight: '800',
    color: textColor,
    marginBottom: 8,
    textAlign: 'center',
    letterSpacing: -0.5,
  },
  headerSubtitle: {
    fontSize: 16,
    color: secondaryTextColor,
    textAlign: 'center',
    lineHeight: 22,
    fontWeight: '500',
  },
  taskInfoCard: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 24,
    padding: 24,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 6,
    },
    shadowOpacity: 0.08,
    shadowRadius: 16,
    elevation: 6,
    borderWidth: 1,
    borderColor: 'rgba(0, 0, 0, 0.03)',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  cardHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  cardHeaderIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  cardHeaderTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: textColor,
  },
  taskStatusBadge: {
    backgroundColor: 'rgba(52, 199, 89, 0.1)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(52, 199, 89, 0.2)',
  },
  taskStatusText: {
    color: successColor,
    fontSize: 14,
    fontWeight: '600',
  },
  taskInfoContent: {
    gap: 16,
  },
  taskInfoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: 'rgba(0, 122, 255, 0.05)',
    borderRadius: 12,
  },
  taskInfoLabel: {
    fontSize: 14,
    color: secondaryTextColor,
    fontWeight: '600',
  },
  taskInfoValue: {
    fontSize: 14,
    color: textColor,
    fontWeight: '600',
  },
  statsContainer: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  sectionTitleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  sectionIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: textColor,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  statsGridSimplified: {
    flexDirection: 'row',
    gap: 16,
    justifyContent: 'space-between',
  },
  statCard: {
    flex: 1,
    minWidth: (screenWidth - 60) / 2 - 6,
    backgroundColor: cardBackgroundColor,
    padding: 20,
    borderRadius: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.08,
    shadowRadius: 12,
    elevation: 4,
    borderWidth: 1,
    borderColor: 'rgba(0, 0, 0, 0.03)',
  },
  statIconContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(0, 122, 255, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  statIcon: {
    fontSize: 24,
  },
  statValue: {
    fontSize: 28,
    fontWeight: '800',
    color: textColor,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 14,
    color: secondaryTextColor,
    fontWeight: '600',
  },
  correctCard: {
    borderColor: 'rgba(52, 199, 89, 0.3)',
    borderWidth: 2,
  },
  correctText: {
    color: successColor,
  },
  accuracyCard: {
    borderColor: 'rgba(88, 86, 214, 0.3)',
    borderWidth: 2,
  },
  questionsSection: {
    marginBottom: 24,
  },
  listContent: {
    paddingBottom: 8,
    gap: 16,
  },
  noDataCard: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 20,
    padding: 40,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.06,
    shadowRadius: 12,
    elevation: 4,
  },
  noDataIconContainer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'rgba(0, 122, 255, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  noDataIcon: {
    fontSize: 32,
  },
  noDataText: {
    fontSize: 18,
    fontWeight: '600',
    color: textColor,
    marginBottom: 8,
    textAlign: 'center',
  },
  noDataSubtext: {
    fontSize: 14,
    color: secondaryTextColor,
    textAlign: 'center',
    lineHeight: 20,
  },
  knowledgeSection: {
    marginBottom: 24,
  },
  simpleSection: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 20,
    padding: 20,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.06,
    shadowRadius: 12,
    elevation: 6,
  },
  simpleSectionHint: {
    fontSize: 16,
    color: secondaryTextColor,
    textAlign: 'center',
    fontStyle: 'italic',
    marginTop: 8,
  },
  knowledgeCard: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 20,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.06,
    shadowRadius: 12,
    elevation: 4,
    borderWidth: 1,
    borderColor: 'rgba(255, 59, 48, 0.1)',
  },
  knowledgeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  knowledgeNumberContainer: {
    backgroundColor: 'rgba(255, 59, 48, 0.1)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  knowledgeNumber: {
    fontSize: 12,
    fontWeight: '600',
    color: errorColor,
  },
  knowledgeTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: textColor,
  },
  knowledgeDescription: {
    fontSize: 14,
    color: secondaryTextColor,
    lineHeight: 20,
  },
  noKnowledgeCard: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 20,
    padding: 40,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.06,
    shadowRadius: 12,
    elevation: 4,
  },
  noKnowledgeIconContainer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'rgba(52, 199, 89, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  noKnowledgeIcon: {
    fontSize: 32,
  },
  noKnowledgeText: {
    fontSize: 18,
    fontWeight: '600',
    color: textColor,
    marginBottom: 8,
    textAlign: 'center',
  },
  noKnowledgeSubtext: {
    fontSize: 14,
    color: secondaryTextColor,
    textAlign: 'center',
    lineHeight: 20,
  },
  suggestionsSection: {
    marginBottom: 40,
  },
  suggestionsCard: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 20,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.06,
    shadowRadius: 12,
    elevation: 4,
    borderWidth: 1,
    borderColor: 'rgba(255, 193, 7, 0.1)',
  },
  suggestionsIconContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(255, 193, 7, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
    alignSelf: 'center',
  },
  suggestionsIcon: {
    fontSize: 24,
  },
  suggestionsTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: textColor,
    marginBottom: 12,
    textAlign: 'center',
  },
  suggestionsContent: {
    fontSize: 15,
    color: secondaryTextColor,
    lineHeight: 22,
    textAlign: 'center',
    fontWeight: '500',
  },
  viewMoreText: {
    fontSize: 14,
    color: primaryColor,
    fontWeight: '600',
  },
  similarQuestionsSection: {
    marginBottom: 40,
  },
  similarQuestionsCard: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 20,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.06,
    shadowRadius: 12,
    elevation: 4,
    borderWidth: 1,
    borderColor: 'rgba(255, 159, 10, 0.1)',
  },
  similarQuestionsIconContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(255, 159, 10, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
    alignSelf: 'center',
  },
  similarQuestionsIcon: {
    fontSize: 24,
  },
  similarQuestionsTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: textColor,
    marginBottom: 12,
    textAlign: 'center',
  },
  similarQuestionsContent: {
    fontSize: 15,
    color: secondaryTextColor,
    lineHeight: 22,
    textAlign: 'center',
    fontWeight: '500',
    marginBottom: 16,
  },
  similarQuestionsPreview: {
    gap: 12,
  },
  previewQuestionCard: {
    backgroundColor: 'rgba(255, 159, 10, 0.05)',
    padding: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#FF9F0A',
  },
  previewQuestionNumber: {
    fontSize: 12,
    fontWeight: '700',
    color: '#FF9F0A',
    marginBottom: 6,
  },
  previewQuestionText: {
    fontSize: 14,
    color: textColor,
    lineHeight: 20,
    fontWeight: '500',
  },
  noSimilarQuestionsCard: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 20,
    padding: 40,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.06,
    shadowRadius: 12,
    elevation: 4,
  },
  noSimilarQuestionsIconContainer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'rgba(0, 122, 255, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  noSimilarQuestionsIcon: {
    fontSize: 32,
  },
  noSimilarQuestionsText: {
    fontSize: 18,
    fontWeight: '600',
    color: textColor,
    marginBottom: 8,
    textAlign: 'center',
  },
  noSimilarQuestionsSubtext: {
    fontSize: 14,
    color: secondaryTextColor,
    textAlign: 'center',
    lineHeight: 20,
  },
});

export default ResultScreen;