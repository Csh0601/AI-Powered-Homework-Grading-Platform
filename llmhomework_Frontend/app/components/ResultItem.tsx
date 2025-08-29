import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import type { CorrectionResult } from '../models/CorrectionResult';
import { 
  successColor, 
  errorColor,
  textColor, 
  secondaryTextColor, 
  cardBackgroundColor,
  borderColor,
  primaryColor,
  warningColor
} from '../styles/colors';

interface ResultItemProps {
  result: CorrectionResult;
}

const ResultItem: React.FC<ResultItemProps> = ({ result }) => {
  // 确保所有字段都有安全的值
  const safeResult = {
    questionId: result.questionId || '未知题目',
    question: result.question || '题目内容缺失',
    userAnswer: result.userAnswer || '未作答',
    correctAnswer: result.correctAnswer || '未知',
    knowledgePoint: result.knowledgePoint || '基础知识点',
    isCorrect: result.isCorrect || false,
    explanation: result.explanation || '',
    score: result.score || 0,
    type: result.type || '未知题型'
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.statusIndicator}>
          <View style={[
            styles.statusIconContainer, 
            safeResult.isCorrect ? styles.correctIconContainer : styles.incorrectIconContainer
          ]}>
            <Text style={[styles.statusIcon, safeResult.isCorrect ? styles.correctIcon : styles.incorrectIcon]}>
              {safeResult.isCorrect ? '✓' : '✗'}
            </Text>
          </View>
        </View>
        <View style={styles.headerInfo}>
          <Text style={styles.questionNumber}>题目 {safeResult.questionId}</Text>
          <Text style={styles.questionType}>{safeResult.type}</Text>
        </View>
        <View style={styles.scoreContainer}>
          <Text style={styles.scoreText}>
            {safeResult.score !== undefined ? safeResult.score.toFixed(1) : '未评分'}
          </Text>
          <Text style={styles.scoreLabel}>分</Text>
        </View>
      </View>

      <View style={styles.content}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>题目内容</Text>
          <View style={styles.sectionContentBox}>
            <Text style={styles.sectionContent}>{safeResult.question}</Text>
          </View>
        </View>

        <View style={styles.answersRow}>
          <View style={styles.answerSection}>
            <Text style={styles.answerLabel}>你的答案</Text>
            <View style={[styles.answerBox, !safeResult.isCorrect && styles.incorrectAnswerBox]}>
              <Text style={[styles.answerText, !safeResult.isCorrect && styles.incorrectAnswerText]}>
                {safeResult.userAnswer}
              </Text>
            </View>
          </View>

          <View style={styles.answerSection}>
            <Text style={styles.answerLabel}>正确答案</Text>
            <View style={[styles.answerBox, styles.correctAnswerBox]}>
              <Text style={[styles.answerText, styles.correctAnswerText]}>
                {safeResult.correctAnswer}
              </Text>
            </View>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>知识点</Text>
          <View style={styles.sectionContentBox}>
            <Text style={styles.sectionContent}>{safeResult.knowledgePoint}</Text>
          </View>
        </View>

        {safeResult.explanation && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>解析</Text>
            <View style={styles.sectionContentBox}>
              <Text style={styles.sectionContent}>{safeResult.explanation}</Text>
            </View>
          </View>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 16,
    marginHorizontal: 20,
    marginVertical: 10,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.08,
    shadowRadius: 12,
    elevation: 4,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0, 0, 0, 0.05)',
  },
  statusIndicator: {
    marginRight: 16,
  },
  statusIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  correctIconContainer: {
    backgroundColor: 'rgba(52, 199, 89, 0.1)',
  },
  incorrectIconContainer: {
    backgroundColor: 'rgba(255, 59, 48, 0.1)',
  },
  statusIcon: {
    fontSize: 20,
    fontWeight: '700',
  },
  correctIcon: {
    color: successColor,
  },
  incorrectIcon: {
    color: errorColor,
  },
  headerInfo: {
    flex: 1,
  },
  questionNumber: {
    fontSize: 18,
    fontWeight: '700',
    color: textColor,
    marginBottom: 4,
  },
  questionType: {
    fontSize: 14,
    color: secondaryTextColor,
    fontWeight: '500',
  },
  scoreContainer: {
    alignItems: 'center',
  },
  scoreText: {
    fontSize: 20,
    fontWeight: '700',
    color: primaryColor,
  },
  scoreLabel: {
    fontSize: 12,
    color: secondaryTextColor,
    marginTop: 2,
  },
  content: {
    padding: 20,
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: textColor,
    marginBottom: 12,
  },
  sectionContentBox: {
    backgroundColor: 'rgba(0, 0, 0, 0.02)',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(0, 0, 0, 0.05)',
  },
  sectionContent: {
    fontSize: 15,
    color: textColor,
    lineHeight: 22,
  },
  answersRow: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 20,
  },
  answerSection: {
    flex: 1,
  },
  answerLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: secondaryTextColor,
    marginBottom: 8,
  },
  answerBox: {
    padding: 12,
    borderRadius: 10,
    borderWidth: 1,
    minHeight: 60,
    justifyContent: 'center',
  },
  correctAnswerBox: {
    backgroundColor: 'rgba(52, 199, 89, 0.05)',
    borderColor: 'rgba(52, 199, 89, 0.2)',
  },
  incorrectAnswerBox: {
    backgroundColor: 'rgba(255, 59, 48, 0.05)',
    borderColor: 'rgba(255, 59, 48, 0.2)',
  },
  answerText: {
    fontSize: 14,
    color: textColor,
    lineHeight: 20,
  },
  correctAnswerText: {
    color: successColor,
  },
  incorrectAnswerText: {
    color: errorColor,
  },
});

export default ResultItem;
