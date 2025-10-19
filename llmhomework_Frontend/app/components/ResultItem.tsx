import React, { useMemo } from 'react';
import { Dimensions, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import type { CorrectionResult } from '../models/CorrectionResult';
import LaTeXRenderer from './LaTeXRenderer';
import {
  successColor,
  errorColor,
  textPrimary,
  textSecondary,
  cardBackground,
  borderColor,
  primaryColor,
  primaryAlpha10,
  successAlpha10,
  errorAlpha10
} from '../styles/colors';
import { typography, spacing, borderRadius, shadows } from '../styles/designSystem';

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
            {renderRichText(safeResult.question, { fontSize: 16, color: textPrimary })}
          </View>
        </View>

        <View style={[styles.answersRow, isNarrowLayout && styles.answersColumn]}>
          <View style={styles.answerSection}>
            <Text style={styles.answerLabel}>你的答案</Text>
            <View style={[styles.answerBox, !safeResult.isCorrect && styles.incorrectAnswerBox]}>
              {renderRichText(safeResult.userAnswer, {
                fontSize: 14,
                color: safeResult.isCorrect ? textPrimary : errorColor
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
            {renderRichText(safeResult.knowledgePoint, { fontSize: 15, color: textPrimary })}
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
              {renderRichText(safeResult.explanation, { fontSize: 15, color: textSecondary })}
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
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    marginHorizontal: 0,
    marginVertical: spacing.md,
    ...shadows.level2,  // 轻柔阴影
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.cardPadding,
    borderBottomWidth: 0.5,  // Apple 精细分割线
    borderBottomColor: borderColor,
  },
  statusIndicator: {
    marginRight: spacing.md,
  },
  statusIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  correctIconContainer: {
    backgroundColor: successAlpha10,
  },
  incorrectIconContainer: {
    backgroundColor: errorAlpha10,
  },
  statusIcon: {
    fontSize: 20,
    fontWeight: '500',  // Apple 中等字重
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
    ...typography.heading3,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.xs / 2,
  },
  questionType: {
    ...typography.bodySmall,
    color: textSecondary,
    fontWeight: '400',
  },
  scoreContainer: {
    alignItems: 'center',
  },
  scoreText: {
    ...typography.heading3,
    fontWeight: '300',  // Apple 轻量字体
    color: primaryColor,
  },
  scoreLabel: {
    ...typography.caption,
    color: textSecondary,
    marginTop: spacing.xs / 2,
  },
  content: {
    padding: spacing.cardPadding,
  },
  section: {
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    ...typography.heading4,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.md,
  },
  sectionContentBox: {
    backgroundColor: primaryAlpha10,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    alignItems: 'flex-start',
    width: '100%',
  },
  sectionContent: {
    ...typography.bodyMedium,
    color: textPrimary,
    alignSelf: 'stretch',
    width: '100%',
    textAlign: 'left',
  },
  answersRow: {
    flexDirection: 'row',
    gap: spacing.md,
    marginBottom: spacing.lg,
  },
  answersColumn: {
    flexDirection: 'column',
  },
  answerSection: {
    flex: 1,
  },
  answerLabel: {
    ...typography.bodySmall,
    fontWeight: '500',
    color: textSecondary,
    marginBottom: spacing.sm,
  },
  answerBox: {
    padding: spacing.md,
    borderRadius: borderRadius.md,
    borderWidth: 0.5,
    width: '100%',
    alignItems: 'flex-start',
    flexDirection: 'column',
  },
  actionButton: {
    marginTop: spacing.md,
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.button,
    backgroundColor: primaryAlpha10,
  },
  actionButtonText: {
    ...typography.caption,
    color: primaryColor,
    fontWeight: '500',
  },
  correctAnswerBox: {
    backgroundColor: successAlpha10,
    borderColor: successColor,
    borderWidth: 0.5,
  },
  incorrectAnswerBox: {
    backgroundColor: errorAlpha10,
    borderColor: errorColor,
    borderWidth: 0.5,
  },
  answerText: {
    ...typography.bodySmall,
    color: textPrimary,
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
