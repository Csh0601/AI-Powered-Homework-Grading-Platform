// 主要问题卡片组件
import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { 
  errorColor, 
  warningColor,
  textColor, 
  secondaryTextColor, 
  cardBackgroundColor,
  borderColor 
} from '../styles/colors';

interface MainIssuesCardProps {
  mainIssues: string[];
  title?: string;
  maxHeight?: number;
}

const MainIssuesCard: React.FC<MainIssuesCardProps> = ({
  mainIssues,
  title = "主要问题",
  maxHeight = 200
}) => {
  if (!mainIssues || mainIssues.length === 0) {
    return null;
  }

  // 根据问题类型分配图标和颜色
  const getIssueStyle = (issue: string, index: number) => {
    const lowerIssue = issue.toLowerCase();
    
    if (lowerIssue.includes('错误') || lowerIssue.includes('mistake') || lowerIssue.includes('wrong')) {
      return { icon: '❌', color: errorColor };
    } else if (lowerIssue.includes('注意') || lowerIssue.includes('warning') || lowerIssue.includes('小心')) {
      return { icon: '⚠️', color: warningColor };
    } else if (lowerIssue.includes('建议') || lowerIssue.includes('recommend') || lowerIssue.includes('改进')) {
      return { icon: '💡', color: '#FF9500' };
    } else {
      return { icon: '🔸', color: errorColor };
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerIcon}>🔍</Text>
        <Text style={styles.title}>{title}</Text>
        <View style={styles.countBadge}>
          <Text style={styles.countText}>{mainIssues.length}</Text>
        </View>
      </View>
      
      <ScrollView 
        style={[styles.scrollContainer, { maxHeight }]}
        showsVerticalScrollIndicator={true}
        nestedScrollEnabled={true}
      >
        <View style={styles.issuesContainer}>
          {mainIssues.map((issue, index) => {
            const issueStyle = getIssueStyle(issue, index);
            return (
              <View key={index} style={styles.issueItem}>
                <Text style={styles.issueIcon}>{issueStyle.icon}</Text>
                <View style={styles.issueContent}>
                  <Text style={styles.issueText}>{issue}</Text>
                  <View style={[styles.priorityLine, { backgroundColor: issueStyle.color }]} />
                </View>
              </View>
            );
          })}
        </View>
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
  countBadge: {
    backgroundColor: errorColor,
    borderRadius: 10,
    paddingHorizontal: 8,
    paddingVertical: 2,
    minWidth: 20,
    alignItems: 'center',
  },
  countText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  scrollContainer: {
    flex: 1,
  },
  issuesContainer: {
    gap: 12,
  },
  issueItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#FFF5F5',
    borderRadius: 8,
    padding: 12,
    borderLeftWidth: 3,
    borderLeftColor: errorColor,
  },
  issueIcon: {
    fontSize: 16,
    marginRight: 10,
    marginTop: 2,
  },
  issueContent: {
    flex: 1,
  },
  issueText: {
    fontSize: 14,
    color: textColor,
    lineHeight: 20,
  },
  priorityLine: {
    height: 2,
    marginTop: 6,
    borderRadius: 1,
    opacity: 0.3,
  },
});

export default MainIssuesCard;
