// 增强的解释卡片组件
import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { 
  primaryColor, 
  successColor, 
  errorColor,
  textColor, 
  secondaryTextColor, 
  cardBackgroundColor,
  borderColor 
} from '../styles/colors';

interface EnhancedExplanationCardProps {
  explanation: string;
  isCorrect: boolean;
  knowledgePoints?: string[];
  correctAnswer?: string;
  maxHeight?: number;
}

const EnhancedExplanationCard: React.FC<EnhancedExplanationCardProps> = ({
  explanation,
  isCorrect,
  knowledgePoints = [],
  correctAnswer,
  maxHeight = 300
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  if (!explanation || explanation.trim() === '') {
    return null;
  }

  const shouldShowExpandButton = explanation.length > 150;
  const displayText = shouldShowExpandButton && !isExpanded 
    ? explanation.substring(0, 150) + '...'
    : explanation;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerIcon}>
          {isCorrect ? '✅' : '❌'}
        </Text>
        <Text style={styles.title}>
          {isCorrect ? '批改说明' : '问题分析'}
        </Text>
        <View style={[
          styles.statusBadge, 
          { backgroundColor: isCorrect ? successColor : errorColor }
        ]}>
          <Text style={styles.statusText}>
            {isCorrect ? '正确' : '错误'}
          </Text>
        </View>
      </View>
      
      <ScrollView 
        style={[styles.contentContainer, { maxHeight }]}
        showsVerticalScrollIndicator={true}
        nestedScrollEnabled={true}
      >
        <Text style={styles.explanationText}>{displayText}</Text>
        
        {shouldShowExpandButton && (
          <TouchableOpacity 
            style={styles.expandButton}
            onPress={() => setIsExpanded(!isExpanded)}
          >
            <Text style={styles.expandButtonText}>
              {isExpanded ? '收起' : '展开全部'}
            </Text>
          </TouchableOpacity>
        )}
        
        {correctAnswer && !isCorrect && (
          <View style={styles.correctAnswerSection}>
            <Text style={styles.correctAnswerLabel}>参考答案：</Text>
            <Text style={styles.correctAnswerText}>{correctAnswer}</Text>
          </View>
        )}
        
        {knowledgePoints.length > 0 && (
          <View style={styles.knowledgeSection}>
            <Text style={styles.knowledgeSectionTitle}>相关知识点：</Text>
            <View style={styles.knowledgePointsContainer}>
              {knowledgePoints.map((point, index) => (
                <View key={index} style={styles.knowledgePointTag}>
                  <Text style={styles.knowledgePointText}>{point}</Text>
                </View>
              ))}
            </View>
          </View>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 12,
    padding: 16,
    marginVertical: 8,
    borderWidth: 1,
    borderColor: borderColor,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  headerIcon: {
    fontSize: 18,
    marginRight: 8,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: textColor,
    flex: 1,
  },
  statusBadge: {
    borderRadius: 10,
    paddingHorizontal: 8,
    paddingVertical: 2,
  },
  statusText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  contentContainer: {
    flex: 1,
  },
  explanationText: {
    fontSize: 14,
    color: textColor,
    lineHeight: 22,
    marginBottom: 8,
  },
  expandButton: {
    alignSelf: 'flex-start',
    paddingVertical: 4,
  },
  expandButtonText: {
    color: primaryColor,
    fontSize: 14,
    fontWeight: '500',
  },
  correctAnswerSection: {
    marginTop: 12,
    padding: 12,
    backgroundColor: '#F0F9FF',
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: successColor,
  },
  correctAnswerLabel: {
    fontSize: 13,
    color: secondaryTextColor,
    fontWeight: '500',
    marginBottom: 4,
  },
  correctAnswerText: {
    fontSize: 14,
    color: textColor,
    lineHeight: 20,
  },
  knowledgeSection: {
    marginTop: 12,
  },
  knowledgeSectionTitle: {
    fontSize: 13,
    color: secondaryTextColor,
    fontWeight: '500',
    marginBottom: 8,
  },
  knowledgePointsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  knowledgePointTag: {
    backgroundColor: primaryColor + '20',
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderWidth: 1,
    borderColor: primaryColor + '40',
  },
  knowledgePointText: {
    fontSize: 12,
    color: primaryColor,
    fontWeight: '500',
  },
});

export default EnhancedExplanationCard;
