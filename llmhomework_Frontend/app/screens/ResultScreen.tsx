import { RouteProp, useRoute } from '@react-navigation/native';
import React, { useEffect, useState } from 'react';
import { FlatList, StyleSheet, Text, View, ScrollView, SafeAreaView, Animated, Dimensions } from 'react-native';
import ResultItem from '../components/ResultItem';
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
  
  // 调试：打印接收到的所有参数
  console.log('🔍 ResultScreen接收到的route.params:', JSON.stringify(route.params, null, 2));
  
  const resultId = route.params?.resultId;
  const gradingResult = route.params?.gradingResult as any;
  const wrongKnowledges = route.params?.wrongKnowledges || [];
  const history = route.params?.history || [];
  const taskId = route.params?.taskId || '未知任务';
  const timestamp = route.params?.timestamp || Date.now();
  
  // 格式化提交时间为可读格式
  const formatSubmissionTime = (timestamp: number) => {
    // 如果时间戳是秒级的（Unix时间戳），转换为毫秒
    const ms = timestamp > 9999999999 ? timestamp : timestamp * 1000;
    const date = new Date(ms);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`;
  };
  
  const submissionTime = formatSubmissionTime(timestamp);
  
  console.log('🔍 解析后的参数:');
  console.log('  - resultId:', resultId);
  console.log('  - gradingResult:', gradingResult ? 'present' : 'missing');
  console.log('  - gradingResult类型:', typeof gradingResult);
  console.log('  - gradingResult长度:', Array.isArray(gradingResult) ? gradingResult.length : 'not array');
  console.log('  - wrongKnowledges:', wrongKnowledges);
  console.log('  - taskId:', taskId);

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

  // 处理gradingResult数据格式
  // gradingResult现在是完整的result对象，包含grading_result和questions
  const questions = gradingResult?.questions || [];
  const gradingResultArray = gradingResult?.grading_result || [];
  const totalScore = gradingResult?.total_score || 0;
  const correctCount = gradingResult?.correct_count || 0;
  const wrongCount = gradingResult?.wrong_count || 0;
  const accuracy = gradingResult?.accuracy || 0;
  
  console.log('🔍 ResultScreen数据处理:');
  console.log('  - questions数组长度:', questions.length);
  console.log('  - grading_result数组长度:', gradingResultArray.length);
  console.log('  - questions内容:', questions);
  console.log('  - grading_result内容:', gradingResultArray);

  // 转换题目数据为CorrectionResult格式
  // 优先使用grading_result数组，因为它包含了批改结果
  const sourceData = gradingResultArray.length > 0 ? gradingResultArray : questions;
  
  const convertedQuestions = sourceData.map((item: any, index: number) => ({
    questionId: item.question_id || `q_${index}`,
    question: item.question || item.stem || `题目${item.number || index + 1}`,
    userAnswer: item.answer || item.user_answer || '未作答',
    correctAnswer: item.correct_answer || '参考答案',
    knowledgePoint: item.knowledge_point || '基础知识点',
    isCorrect: item.correct || item.is_correct || false,
    explanation: item.explanation || '暂无解析',
    score: item.score || 0,
    type: item.type || '填空题'
  }));
  
  console.log('🔍 转换后的题目数据:');
  console.log('  - 源数据来源:', gradingResultArray.length > 0 ? 'grading_result' : 'questions');
  console.log('  - 转换后题目数量:', convertedQuestions.length);
  console.log('  - 转换后数据:', convertedQuestions);

  // 计算统计数据
  const actualCorrectCount = convertedQuestions.filter((q: any) => q.isCorrect).length;
  const actualWrongCount = convertedQuestions.filter((q: any) => !q.isCorrect).length;
  const actualTotalScore = convertedQuestions.reduce((sum: number, q: any) => sum + (q.score || 0), 0);
  const actualAccuracy = convertedQuestions.length > 0 ? (actualCorrectCount / convertedQuestions.length) * 100 : 0;

  // 如果没有题目数据，显示提示信息
  if (convertedQuestions.length === 0) {
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
            <View style={styles.statsGrid}>
              <View style={[styles.statCard, styles.totalScoreCard]}>
                <View style={styles.statIconContainer}>
                  <Text style={styles.statIcon}>🏆</Text>
                </View>
                <Text style={styles.statValue}>{actualTotalScore.toFixed(1)}</Text>
                <Text style={styles.statLabel}>总分</Text>
              </View>
              <View style={[styles.statCard, styles.correctCard]}>
                <View style={styles.statIconContainer}>
                  <Text style={styles.statIcon}>✅</Text>
                </View>
                <Text style={[styles.statValue, styles.correctText]}>{actualCorrectCount}</Text>
                <Text style={styles.statLabel}>正确</Text>
              </View>
              <View style={[styles.statCard, styles.incorrectCard]}>
                <View style={styles.statIconContainer}>
                  <Text style={styles.statIcon}>❌</Text>
                </View>
                <Text style={[styles.statValue, styles.incorrectText]}>{actualWrongCount}</Text>
                <Text style={styles.statLabel}>错误</Text>
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
            {convertedQuestions.length > 0 ? (
              <FlatList
                data={convertedQuestions}
                keyExtractor={(item) => item.questionId}
                renderItem={({ item }) => <ResultItem result={item as CorrectionResult} />}
                contentContainerStyle={styles.list}
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

          {/* 错题知识点分析 */}
          <View style={styles.knowledgeSection}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionIcon}>🧠</Text>
              <Text style={styles.sectionTitle}>错题知识点分析</Text>
            </View>
            {wrongKnowledges.length > 0 ? (
              wrongKnowledges.map((knowledge: any, index: number) => (
                <View key={index} style={styles.knowledgeCard}>
                  <View style={styles.knowledgeHeader}>
                    <View style={styles.knowledgeNumberContainer}>
                      <Text style={styles.knowledgeNumber}>
                        第{knowledge.question_number || index + 1}题
                      </Text>
                    </View>
                    <Text style={styles.knowledgeTitle}>
                      {knowledge.knowledge_point || '知识点'}
                    </Text>
                  </View>
                  <Text style={styles.knowledgeDescription}>
                    {knowledge.description || '该知识点需要加强练习'}
                  </Text>
                </View>
              ))
            ) : (
              <View style={styles.noKnowledgeCard}>
                <View style={styles.noKnowledgeIconContainer}>
                  <Text style={styles.noKnowledgeIcon}>🎉</Text>
                </View>
                <Text style={styles.noKnowledgeText}>恭喜！没有错题知识点</Text>
                <Text style={styles.noKnowledgeSubtext}>继续保持，继续进步</Text>
              </View>
            )}
          </View>

          {/* 学习建议 */}
          <View style={styles.suggestionsSection}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionIcon}>💡</Text>
              <Text style={styles.sectionTitle}>学习建议</Text>
            </View>
            <View style={styles.suggestionsCard}>
              <View style={styles.suggestionsIconContainer}>
                <Text style={styles.suggestionsIcon}>💡</Text>
              </View>
              <Text style={styles.suggestionsTitle}>个性化学习建议</Text>
              <Text style={styles.suggestionsContent}>
                {actualAccuracy >= 80 
                  ? '🎉 表现优秀！建议继续保持当前的学习状态，可以尝试更有挑战性的题目。'
                  : actualAccuracy >= 60
                  ? '👍 表现良好！建议重点复习错题，巩固薄弱知识点，多做相关练习。'
                  : '📚 需要加强！建议系统复习相关知识点，多做基础练习，建立扎实的基础。'
                }
              </Text>
            </View>
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
    marginBottom: 20,
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
  totalScoreCard: {
    borderColor: 'rgba(255, 193, 7, 0.3)',
    borderWidth: 2,
  },
  correctCard: {
    borderColor: 'rgba(52, 199, 89, 0.3)',
    borderWidth: 2,
  },
  correctText: {
    color: successColor,
  },
  incorrectCard: {
    borderColor: 'rgba(255, 59, 48, 0.3)',
    borderWidth: 2,
  },
  incorrectText: {
    color: errorColor,
  },
  accuracyCard: {
    borderColor: 'rgba(88, 86, 214, 0.3)',
    borderWidth: 2,
  },
  questionsSection: {
    marginBottom: 24,
  },
  list: {
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
});

export default ResultScreen;
