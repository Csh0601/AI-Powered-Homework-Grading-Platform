import React, { useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { HistoryRecord } from '../types/HistoryTypes';
import {
  primaryColor,
  textColor,
  secondaryTextColor,
  backgroundColor,
  cardBackgroundColor,
  borderColor,
  successColor,
  errorColor,
  systemBlue,
  systemOrange,
  systemPurple,
} from '../styles/colors';

interface LearningInsightsProps {
  records: HistoryRecord[];
  onRecommendationPress?: (recommendation: LearningRecommendation) => void;
}

interface LearningRecommendation {
  id: string;
  type: 'knowledge' | 'practice' | 'schedule' | 'strategy';
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  actionText?: string;
  icon: string;
  color: string;
}

interface LearningPattern {
  studyFrequency: 'daily' | 'frequent' | 'occasional' | 'rare';
  performanceTrend: 'improving' | 'stable' | 'declining';
  strongSubjects: string[];
  weakSubjects: string[];
  optimalStudyTime: string;
  averageSessionLength: number;
}

const LearningInsights: React.FC<LearningInsightsProps> = ({
  records,
  onRecommendationPress,
}) => {
  // 分析学习模式
  const learningPattern = useMemo((): LearningPattern => {
    if (!records || records.length === 0) {
      return {
        studyFrequency: 'rare',
        performanceTrend: 'stable',
        strongSubjects: [],
        weakSubjects: [],
        optimalStudyTime: '未知',
        averageSessionLength: 0,
      };
    }

    // 分析学习频率
    const now = Date.now();
    const recentRecords = records.filter(r => now - r.timestamp < 30 * 24 * 60 * 60 * 1000); // 最近30天
    let studyFrequency: LearningPattern['studyFrequency'] = 'rare';
    
    if (recentRecords.length >= 20) {
      studyFrequency = 'daily';
    } else if (recentRecords.length >= 10) {
      studyFrequency = 'frequent';
    } else if (recentRecords.length >= 3) {
      studyFrequency = 'occasional';
    }

    // 分析表现趋势
    let performanceTrend: LearningPattern['performanceTrend'] = 'stable';
    if (records.length >= 3) {
      const recent = records.slice(0, Math.min(3, records.length));
      const older = records.slice(Math.min(3, records.length), Math.min(6, records.length));
      
      if (recent.length > 0 && older.length > 0) {
        const recentAvg = recent.reduce((sum, r) => {
          if (!r.summary || r.summary.totalQuestions === 0) return sum;
          return sum + (r.summary.correctCount / r.summary.totalQuestions);
        }, 0) / recent.length;
        
        const olderAvg = older.reduce((sum, r) => {
          if (!r.summary || r.summary.totalQuestions === 0) return sum;
          return sum + (r.summary.correctCount / r.summary.totalQuestions);
        }, 0) / older.length;
        
        const improvement = recentAvg - olderAvg;
        if (improvement > 0.1) {
          performanceTrend = 'improving';
        } else if (improvement < -0.1) {
          performanceTrend = 'declining';
        }
      }
    }

    // 分析学习时间偏好
    const hourCounts: { [hour: number]: number } = {};
    records.forEach(record => {
      const hour = new Date(record.timestamp).getHours();
      hourCounts[hour] = (hourCounts[hour] || 0) + 1;
    });
    
    const optimalHour = Object.entries(hourCounts)
      .sort(([,a], [,b]) => b - a)[0]?.[0];
    
    let optimalStudyTime = '未知';
    if (optimalHour) {
      const hour = parseInt(optimalHour);
      if (hour >= 6 && hour < 12) {
        optimalStudyTime = '上午 (6:00-12:00)';
      } else if (hour >= 12 && hour < 18) {
        optimalStudyTime = '下午 (12:00-18:00)';
      } else {
        optimalStudyTime = '晚上 (18:00-6:00)';
      }
    }

    // 分析知识点强弱
    const knowledgeStats: { [key: string]: { total: number; correct: number } } = {};
    records.forEach(record => {
      if (record.wrongKnowledges) {
        record.wrongKnowledges.forEach((knowledge: any) => {
          const point = knowledge.knowledge_point || '其他';
          if (!knowledgeStats[point]) {
            knowledgeStats[point] = { total: 0, correct: 0 };
          }
          knowledgeStats[point].total++;
        });
      }
    });

    const weakSubjects = Object.entries(knowledgeStats)
      .filter(([, stats]) => stats.total >= 2) // 至少出现2次的知识点
      .sort(([,a], [,b]) => b.total - a.total)
      .slice(0, 3)
      .map(([point]) => point);

    return {
      studyFrequency,
      performanceTrend,
      strongSubjects: [], // 这里可以进一步分析
      weakSubjects,
      optimalStudyTime,
      averageSessionLength: records.length > 0 ? Math.round(records.reduce((sum, r) => 
        sum + (r.summary?.totalQuestions || 0), 0) / records.length) : 0,
    };
  }, [records]);

  // 生成学习建议
  const recommendations = useMemo((): LearningRecommendation[] => {
    const recs: LearningRecommendation[] = [];

    // 基于表现趋势的建议
    if (learningPattern.performanceTrend === 'declining') {
      recs.push({
        id: 'performance_decline',
        type: 'strategy',
        title: '表现下降趋势',
        description: '最近的学习表现有所下降，建议调整学习策略，增加复习频率。',
        priority: 'high',
        actionText: '制定复习计划',
        icon: '📉',
        color: errorColor,
      });
    } else if (learningPattern.performanceTrend === 'improving') {
      recs.push({
        id: 'performance_improving',
        type: 'strategy',
        title: '表现持续改善',
        description: '学习状态很好！保持当前的学习节奏，可以适当增加难度。',
        priority: 'low',
        actionText: '挑战更难题目',
        icon: '📈',
        color: successColor,
      });
    }

    // 基于学习频率的建议
    if (learningPattern.studyFrequency === 'rare') {
      recs.push({
        id: 'increase_frequency',
        type: 'schedule',
        title: '增加学习频率',
        description: '建议增加学习频率，每天至少完成一套练习，培养学习习惯。',
        priority: 'high',
        actionText: '设置学习提醒',
        icon: '⏰',
        color: systemOrange,
      });
    } else if (learningPattern.studyFrequency === 'daily') {
      recs.push({
        id: 'maintain_habit',
        type: 'schedule',
        title: '保持学习习惯',
        description: '您的学习频率很好！继续保持每日学习的好习惯。',
        priority: 'low',
        actionText: '继续保持',
        icon: '✅',
        color: successColor,
      });
    }

    // 基于薄弱知识点的建议
    if (learningPattern.weakSubjects.length > 0) {
      recs.push({
        id: 'weak_subjects',
        type: 'knowledge',
        title: '重点复习薄弱知识点',
        description: `建议重点复习: ${learningPattern.weakSubjects.slice(0, 2).join('、')}等知识点。`,
        priority: 'high',
        actionText: '开始专项练习',
        icon: '🎯',
        color: primaryColor,
      });
    }

    // 基于学习时间的建议
    if (learningPattern.optimalStudyTime !== '未知') {
      recs.push({
        id: 'optimal_time',
        type: 'schedule',
        title: '最佳学习时间',
        description: `根据您的学习记录，${learningPattern.optimalStudyTime}是您的高效学习时段。`,
        priority: 'medium',
        actionText: '安排学习时间',
        icon: '🕐',
        color: systemBlue,
      });
    }

    // 基于题目数量的建议
    if (learningPattern.averageSessionLength < 5) {
      recs.push({
        id: 'increase_volume',
        type: 'practice',
        title: '增加练习量',
        description: '建议每次练习增加题目数量，提高学习效率和知识覆盖面。',
        priority: 'medium',
        actionText: '增加练习题数',
        icon: '📚',
        color: systemPurple,
      });
    } else if (learningPattern.averageSessionLength > 15) {
      recs.push({
        id: 'balance_practice',
        type: 'practice',
        title: '平衡练习强度',
        description: '练习量很充足，注意劳逸结合，保持学习效率。',
        priority: 'low',
        actionText: '适当休息',
        icon: '⚖️',
        color: systemBlue,
      });
    }

    // 通用建议
    if (records.length >= 10) {
      recs.push({
        id: 'review_errors',
        type: 'strategy',
        title: '定期回顾错题',
        description: '建议定期回顾历史错题，巩固薄弱知识点，避免重复错误。',
        priority: 'medium',
        actionText: '查看错题集',
        icon: '🔄',
        color: systemOrange,
      });
    }

    return recs.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
  }, [learningPattern, records.length]);

  // 学习统计卡片
  const renderStatsCard = () => (
    <View style={styles.statsCard}>
      <Text style={styles.sectionTitle}>📊 学习统计分析</Text>
      
      <View style={styles.statsGrid}>
        <View style={styles.statItem}>
          <Text style={styles.statIcon}>📅</Text>
          <Text style={styles.statLabel}>学习频率</Text>
          <Text style={styles.statValue}>
            {learningPattern.studyFrequency === 'daily' ? '每日学习' :
             learningPattern.studyFrequency === 'frequent' ? '经常学习' :
             learningPattern.studyFrequency === 'occasional' ? '偶尔学习' : '较少学习'}
          </Text>
        </View>
        
        <View style={styles.statItem}>
          <Text style={styles.statIcon}>
            {learningPattern.performanceTrend === 'improving' ? '📈' :
             learningPattern.performanceTrend === 'declining' ? '📉' : '📊'}
          </Text>
          <Text style={styles.statLabel}>表现趋势</Text>
          <Text style={[
            styles.statValue,
            { color: learningPattern.performanceTrend === 'improving' ? successColor :
                     learningPattern.performanceTrend === 'declining' ? errorColor : textColor }
          ]}>
            {learningPattern.performanceTrend === 'improving' ? '持续改善' :
             learningPattern.performanceTrend === 'declining' ? '需要努力' : '保持稳定'}
          </Text>
        </View>
        
        <View style={styles.statItem}>
          <Text style={styles.statIcon}>🕐</Text>
          <Text style={styles.statLabel}>最佳时段</Text>
          <Text style={styles.statValue}>{learningPattern.optimalStudyTime}</Text>
        </View>
        
        <View style={styles.statItem}>
          <Text style={styles.statIcon}>📝</Text>
          <Text style={styles.statLabel}>平均题数</Text>
          <Text style={styles.statValue}>{learningPattern.averageSessionLength} 题</Text>
        </View>
      </View>
    </View>
  );

  // 建议卡片
  const renderRecommendations = () => (
    <View style={styles.recommendationsCard}>
      <Text style={styles.sectionTitle}>💡 个性化学习建议</Text>
      
      {recommendations.length === 0 ? (
        <View style={styles.noRecommendations}>
          <Text style={styles.noRecommendationsText}>
            暂无特别建议，请继续保持学习！
          </Text>
        </View>
      ) : (
        recommendations.map((rec) => (
          <TouchableOpacity
            key={rec.id}
            style={[styles.recommendationItem, { borderLeftColor: rec.color }]}
            onPress={() => onRecommendationPress?.(rec)}
            activeOpacity={0.7}
          >
            <View style={styles.recommendationHeader}>
              <View style={styles.recommendationTitle}>
                <Text style={styles.recommendationIcon}>{rec.icon}</Text>
                <Text style={styles.recommendationTitleText}>{rec.title}</Text>
              </View>
              <View style={[styles.priorityBadge, {
                backgroundColor: rec.priority === 'high' ? errorColor :
                                rec.priority === 'medium' ? systemOrange : successColor
              }]}>
                <Text style={styles.priorityText}>
                  {rec.priority === 'high' ? '高' :
                   rec.priority === 'medium' ? '中' : '低'}
                </Text>
              </View>
            </View>
            
            <Text style={styles.recommendationDescription}>
              {rec.description}
            </Text>
            
            {rec.actionText && (
              <Text style={styles.recommendationAction}>
                👉 {rec.actionText}
              </Text>
            )}
          </TouchableOpacity>
        ))
      )}
    </View>
  );

  // 薄弱知识点
  const renderWeakSubjects = () => {
    if (learningPattern.weakSubjects.length === 0) return null;
    
    return (
      <View style={styles.weakSubjectsCard}>
        <Text style={styles.sectionTitle}>🎯 需要加强的知识点</Text>
        
        <View style={styles.subjectsList}>
          {learningPattern.weakSubjects.map((subject, index) => (
            <View key={subject} style={styles.subjectItem}>
              <Text style={styles.subjectRank}>{index + 1}</Text>
              <Text style={styles.subjectName}>{subject}</Text>
              <Text style={styles.subjectHint}>需要重点复习</Text>
            </View>
          ))}
        </View>
      </View>
    );
  };

  if (!records || records.length === 0) {
    return (
      <View style={styles.container}>
        <View style={styles.emptyState}>
          <Text style={styles.emptyIcon}>📊</Text>
          <Text style={styles.emptyTitle}>暂无学习数据</Text>
          <Text style={styles.emptyDescription}>
            完成更多练习后，这里将显示个性化的学习洞察和建议
          </Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView 
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
        bounces={false}
        decelerationRate="fast"
        scrollEventThrottle={16}
        style={styles.scrollView}
      >
        {renderStatsCard()}
        {renderRecommendations()}
        {renderWeakSubjects()}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 16,
    margin: 16,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: borderColor,
    maxHeight: 400, // 设置最大高度，确保有滚动空间
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingBottom: 16, // 确保底部内容可见
  },
  emptyState: {
    alignItems: 'center',
    padding: 40,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: textColor,
    marginBottom: 8,
  },
  emptyDescription: {
    fontSize: 14,
    color: secondaryTextColor,
    textAlign: 'center',
    lineHeight: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: textColor,
    marginBottom: 16,
  },
  statsCard: {
    padding: 20,
    backgroundColor: backgroundColor,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
  },
  statItem: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    flex: 1,
    minWidth: '45%',
    borderWidth: 1,
    borderColor: borderColor,
  },
  statIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  statLabel: {
    fontSize: 12,
    color: secondaryTextColor,
    marginBottom: 4,
    textAlign: 'center',
  },
  statValue: {
    fontSize: 14,
    fontWeight: '600',
    color: textColor,
    textAlign: 'center',
  },
  recommendationsCard: {
    padding: 20,
    backgroundColor: backgroundColor,
  },
  noRecommendations: {
    alignItems: 'center',
    padding: 20,
  },
  noRecommendationsText: {
    fontSize: 14,
    color: secondaryTextColor,
    textAlign: 'center',
  },
  recommendationItem: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderWidth: 1,
    borderColor: borderColor,
  },
  recommendationHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  recommendationTitle: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  recommendationIcon: {
    fontSize: 18,
    marginRight: 8,
  },
  recommendationTitleText: {
    fontSize: 16,
    fontWeight: '600',
    color: textColor,
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  priorityText: {
    fontSize: 10,
    color: '#fff',
    fontWeight: '600',
  },
  recommendationDescription: {
    fontSize: 14,
    color: secondaryTextColor,
    lineHeight: 20,
    marginBottom: 8,
  },
  recommendationAction: {
    fontSize: 12,
    color: primaryColor,
    fontWeight: '500',
  },
  weakSubjectsCard: {
    padding: 20,
    backgroundColor: backgroundColor,
  },
  subjectsList: {
    gap: 12,
  },
  subjectItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: cardBackgroundColor,
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: borderColor,
  },
  subjectRank: {
    fontSize: 18,
    fontWeight: '700',
    color: errorColor,
    marginRight: 16,
    minWidth: 24,
    textAlign: 'center',
  },
  subjectName: {
    fontSize: 16,
    fontWeight: '500',
    color: textColor,
    flex: 1,
  },
  subjectHint: {
    fontSize: 12,
    color: secondaryTextColor,
  },
});

export default LearningInsights;
