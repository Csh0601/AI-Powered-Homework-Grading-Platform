import { RouteProp, useRoute } from '@react-navigation/native';
import React from 'react';
import { FlatList, SafeAreaView, StyleSheet, Text, View, ScrollView, TouchableOpacity } from 'react-native';
import { RootStackParamList } from '../navigation/NavigationTypes';
import { cardBackgroundColor, primaryColor, secondaryTextColor, textColor, backgroundColor } from '../styles/colors';

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
  questionsSection: {
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
    flex: 1,
  },
  questionCount: {
    fontSize: 14,
    color: primaryColor,
    fontWeight: '600',
    backgroundColor: 'rgba(88, 86, 214, 0.1)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  listContent: {
    gap: 16,
  },
  questionCard: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 24,
    padding: 24,
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
  questionNumberContainer: {
    backgroundColor: 'rgba(88, 86, 214, 0.1)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 16,
  },
  questionNumber: {
    fontSize: 14,
    fontWeight: '700',
    color: primaryColor,
  },
  typeContainer: {
    backgroundColor: 'rgba(52, 199, 89, 0.1)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  typeText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#34C759',
  },
  questionSection: {
    marginBottom: 16,
  },
  sectionTitleLocal: {
    fontSize: 16,
    fontWeight: '700',
    color: textColor,
    marginBottom: 12,
  },
  questionText: {
    fontSize: 15,
    color: textColor,
    lineHeight: 22,
    fontWeight: '500',
    backgroundColor: 'rgba(0, 122, 255, 0.05)',
    padding: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
  },
  divider: {
    height: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.06)',
    marginVertical: 16,
  },
  similarQuestionText: {
    fontSize: 15,
    color: textColor,
    lineHeight: 22,
    fontWeight: '500',
    backgroundColor: 'rgba(255, 193, 7, 0.05)',
    padding: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#FFC107',
  },
  practiceHint: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(52, 199, 89, 0.05)',
    padding: 16,
    borderRadius: 12,
    marginTop: 8,
  },
  hintIconContainer: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(52, 199, 89, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  hintIcon: {
    fontSize: 16,
  },
  hintText: {
    fontSize: 14,
    color: '#34C759',
    fontWeight: '600',
    flex: 1,
  },
  emptyCard: {
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
  emptyIconContainer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'rgba(0, 122, 255, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  emptyIcon: {
    fontSize: 32,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: textColor,
    marginBottom: 8,
    textAlign: 'center',
  },
  emptySubtext: {
    fontSize: 14,
    color: secondaryTextColor,
    textAlign: 'center',
    lineHeight: 20,
  },
  tipsSection: {
    marginBottom: 40,
  },
  tipCard: {
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
  tipIconContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(255, 193, 7, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
    alignSelf: 'center',
  },
  tipIcon: {
    fontSize: 24,
  },
  tipTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: textColor,
    marginBottom: 12,
    textAlign: 'center',
  },
  tipContent: {
    fontSize: 15,
    color: secondaryTextColor,
    lineHeight: 22,
    fontWeight: '500',
  },
});

export default SimilarQuestionsScreen;
