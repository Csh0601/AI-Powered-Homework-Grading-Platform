import React, { useMemo } from 'react';
import { Dimensions, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import type { CorrectionResult } from '../models/CorrectionResult';
import LaTeXRenderer from './LaTeXRenderer';
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
  onPressExplanation?: () => void;
  onPressKnowledge?: () => void;
}

const ResultItem: React.FC<ResultItemProps> = ({ result, onPressExplanation, onPressKnowledge }) => {
  const windowWidth = Dimensions.get('window').width;
  const isNarrowLayout = windowWidth < 360;

  const hasLaTeX = (text: string): boolean => {
    if (!text) return false;
    return /\\[a-zA-Z]+\{.*?\}|\\frac|\\times|\\div|\^|_|\$/.test(text);
  };

  const renderRichText = (content: string, options?: { color?: string; fontSize?: number }) => {
    const trimmed = content?.trim?.() ?? '';
    if (!trimmed) {
      return <Text style={[styles.sectionContent, options && { color: options.color }]}>{'暂无内容'}</Text>;
    }

    // 暂时禁用LaTeX渲染，直接显示文本内容
    // 将LaTeX语法转换为可读文本
    const convertLaTeXToText = (text: string): string => {
      return text
        .replace(/\\times/g, '×')
        .replace(/\\div/g, '÷')
        .replace(/\\frac\{([^}]+)\}\{([^}]+)\}/g, '($1/$2)')
        .replace(/\^(\d+)/g, '^$1')
        .replace(/\^\{([^}]+)\}/g, '^($1)');
    };

    const displayText = hasLaTeX(trimmed) ? convertLaTeXToText(trimmed) : trimmed;

    return (
      <Text style={[styles.sectionContent, options && { color: options.color }]}>{displayText}</Text>
    );
  };

  const safeResult = useMemo(() => {
    return {
      questionId: result.questionId || '未知题目',
      question: result.question || '题目内容缺失',
      userAnswer: result.userAnswer || '未作答',
      correctAnswer: result.correctAnswer || '参考答案',
      knowledgePoint: result.knowledgePoint || '基础知识点',
      knowledgePoints: result.knowledgePoints || [],
      isCorrect: Boolean(result.isCorrect),
      explanation: result.explanation || '',
      score: typeof result.score === 'number' ? result.score : Number(result.score) || 0,
      type: result.type || '未知题型'
    };
  }, [result]);

  return (
    <View style={[styles.container, isNarrowLayout && styles.containerNarrow]}>
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
            {renderRichText(safeResult.question, { fontSize: 16, color: textColor })}
          </View>
        </View>

        <View style={[styles.answersRow, isNarrowLayout && styles.answersColumn]}>
          <View style={styles.answerSection}>
            <Text style={styles.answerLabel}>你的答案</Text>
            <View style={[styles.answerBox, !safeResult.isCorrect && styles.incorrectAnswerBox]}>
              {renderRichText(safeResult.userAnswer, {
                fontSize: 14,
                color: safeResult.isCorrect ? textColor : errorColor
              })}
            </View>
          </View>

          <View style={styles.answerSection}>
            <Text style={styles.answerLabel}>正确答案</Text>
            <View style={[styles.answerBox, styles.correctAnswerBox]}>
              {renderRichText(safeResult.correctAnswer, {
                fontSize: 14,
                color: successColor
              })}
            </View>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>知识点</Text>
          <View style={styles.sectionContentBox}>
            {renderRichText(safeResult.knowledgePoint, { fontSize: 15, color: textColor })}
          </View>
          {onPressKnowledge && (
            <TouchableOpacity style={styles.actionButton} onPress={onPressKnowledge}>
              <Text style={styles.actionButtonText}>查看知识点详情</Text>
            </TouchableOpacity>
          )}
        </View>

        {safeResult.explanation && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>解析</Text>
            <View style={styles.sectionContentBox}>
              {renderRichText(safeResult.explanation, { fontSize: 15, color: secondaryTextColor })}
            </View>
            {onPressExplanation && (
              <TouchableOpacity style={styles.actionButton} onPress={onPressExplanation}>
                <Text style={styles.actionButtonText}>查看详细解析</Text>
              </TouchableOpacity>
            )}
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
    marginHorizontal: 0,
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
    alignItems: 'flex-start',
    width: '100%',
  },
  sectionContent: {
    fontSize: 15,
    color: textColor,
    lineHeight: 22,
    alignSelf: 'stretch',
    width: '100%',
    textAlign: 'left',
  },
  answersRow: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 20,
  },
  answersColumn: {
    flexDirection: 'column',
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
    width: '100%',
    alignItems: 'flex-start',
    flexDirection: 'column',
  },
  actionButton: {
    marginTop: 12,
    alignSelf: 'flex-start',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 12,
    backgroundColor: 'rgba(88, 86, 214, 0.1)',
  },
  actionButtonText: {
    fontSize: 13,
    color: primaryColor,
    fontWeight: '600',
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
    flexShrink: 1,
    width: '100%',
    textAlign: 'left',
  },
  correctAnswerText: {
    color: successColor,
  },
  incorrectAnswerText: {
    color: errorColor,
  },
  explanationText: {
    lineHeight: 24,
    fontFamily: 'System',
  },
  containerNarrow: {
    marginHorizontal: 0,
  }
});

export default ResultItem;
