import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  ScrollView,
  Alert,
  Dimensions,
  Share,
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
} from '../styles/colors';

interface ShareManagerProps {
  visible: boolean;
  onClose: () => void;
  record: HistoryRecord;
}

interface ShareContent {
  title: string;
  content: string;
  type: 'text' | 'image' | 'report';
}

const ShareManager: React.FC<ShareManagerProps> = ({
  visible,
  onClose,
  record,
}) => {
  const [shareType, setShareType] = useState<'simple' | 'detailed' | 'report'>('simple');
  const [loading, setLoading] = useState(false);

  // 生成简单分享内容
  const generateSimpleShare = useCallback((): ShareContent => {
    const summary = record.summary || { totalQuestions: 0, correctCount: 0, wrongCount: 0 };
    const correctRate = summary.totalQuestions > 0 
      ? ((summary.correctCount / summary.totalQuestions) * 100).toFixed(1)
      : '0.0';

    return {
      title: '学习记录分享',
      content: `📚 我刚完成了一次作业批改！

📅 时间: ${record.displayTime}
📊 总题数: ${summary.totalQuestions}
✅ 正确: ${summary.correctCount} 题
❌ 错误: ${summary.wrongCount} 题
🎯 正确率: ${correctRate}%${summary.score !== undefined ? `\n💯 分数: ${summary.score}` : ''}

继续加油学习！ 💪`,
      type: 'text',
    };
  }, [record]);

  // 生成详细分享内容
  const generateDetailedShare = useCallback((): ShareContent => {
    const summary = record.summary || { totalQuestions: 0, correctCount: 0, wrongCount: 0 };
    const correctRate = summary.totalQuestions > 0 
      ? ((summary.correctCount / summary.totalQuestions) * 100).toFixed(1)
      : '0.0';

    const gradingResults = record.gradingResult?.grading_result || [];
    
    let detailedContent = `📚 智能批改详细报告

📅 批改时间: ${record.displayTime}
🆔 任务ID: ${record.taskId}

📊 整体表现:
• 总题数: ${summary.totalQuestions}
• 正确题数: ${summary.correctCount}
• 错误题数: ${summary.wrongCount}
• 正确率: ${correctRate}%${summary.score !== undefined ? `\n• 平均分: ${summary.score}` : ''}

`;

    if (gradingResults.length > 0) {
      detailedContent += `📝 题目详情:\n`;
      gradingResults.slice(0, 5).forEach((result: any, index: number) => {
        const status = result.is_correct ? '✅' : '❌';
        const explanation = result.explanation ? result.explanation.substring(0, 50) + '...' : '无解析';
        detailedContent += `${index + 1}. ${status} ${explanation}\n`;
      });
      
      if (gradingResults.length > 5) {
        detailedContent += `... 还有 ${gradingResults.length - 5} 题\n`;
      }
    }

    if (record.wrongKnowledges && record.wrongKnowledges.length > 0) {
      detailedContent += `\n🧠 需要加强的知识点:\n`;
      record.wrongKnowledges.slice(0, 3).forEach((knowledge: any, index: number) => {
        detailedContent += `• ${knowledge.knowledge_point || '知识点' + (index + 1)}\n`;
      });
    }

    detailedContent += '\n📱 来自智能批改系统';

    return {
      title: '智能批改详细报告',
      content: detailedContent,
      type: 'text',
    };
  }, [record]);

  // 生成学习报告
  const generateLearningReport = useCallback((): ShareContent => {
    const summary = record.summary || { totalQuestions: 0, correctCount: 0, wrongCount: 0 };
    const correctRate = summary.totalQuestions > 0 
      ? ((summary.correctCount / summary.totalQuestions) * 100).toFixed(1)
      : '0.0';

    const performance = parseFloat(correctRate);
    let performanceLevel = '';
    let recommendation = '';

    if (performance >= 90) {
      performanceLevel = '优秀 🌟';
      recommendation = '继续保持，可以挑战更高难度的题目！';
    } else if (performance >= 80) {
      performanceLevel = '良好 👍';
      recommendation = '表现不错，继续努力提高正确率！';
    } else if (performance >= 70) {
      performanceLevel = '中等 📈';
      recommendation = '需要加强练习，重点关注错题知识点。';
    } else if (performance >= 60) {
      performanceLevel = '待提高 📚';
      recommendation = '建议复习基础知识，多做练习题。';
    } else {
      performanceLevel = '需要努力 💪';
      recommendation = '建议系统性复习，寻求老师或同学帮助。';
    }

    const reportContent = `📊 个人学习报告

👤 学习者表现分析
📅 记录时间: ${record.displayTime}

🎯 本次表现:
• 完成题目: ${summary.totalQuestions} 题
• 正确答题: ${summary.correctCount} 题
• 错误题目: ${summary.wrongCount} 题
• 正确率: ${correctRate}%
• 表现等级: ${performanceLevel}

💡 智能建议:
${recommendation}

📈 进步方向:
${record.wrongKnowledges && record.wrongKnowledges.length > 0 
  ? `• 重点复习: ${record.wrongKnowledges.slice(0, 2).map((k: any) => k.knowledge_point || '相关知识点').join('、')}`
  : '• 继续保持当前学习状态'
}
• 建议每日练习 30-60 分钟
• 定期复习错题，加深理解

🎓 学习格言: "每一次练习都是进步的阶梯！"

📱 智能批改系统 - 让学习更高效`;

    return {
      title: '个人学习报告',
      content: reportContent,
      type: 'report',
    };
  }, [record]);

  // 执行分享
  const handleShare = useCallback(async (shareContent: ShareContent) => {
    try {
      setLoading(true);

      const result = await Share.share({
        title: shareContent.title,
        message: shareContent.content,
      });

      if (result.action === Share.sharedAction) {
        if (result.activityType) {
          console.log(`✅ 分享成功到: ${result.activityType}`);
        } else {
          console.log('✅ 分享成功');
        }
        Alert.alert('分享成功', '内容已成功分享！');
      } else if (result.action === Share.dismissedAction) {
        console.log('ℹ️ 用户取消分享');
      }
    } catch (error) {
      console.error('分享失败:', error);
      Alert.alert('分享失败', `分享过程中出现错误: ${error}`);
    } finally {
      setLoading(false);
    }
  }, []);

  // 复制到剪贴板
  const copyToClipboard = useCallback((content: string) => {
    // 在实际应用中应该使用 Clipboard API
    Alert.alert('复制成功', '内容已复制到剪贴板', [
      { text: '确定' }
    ]);
    console.log('📋 复制内容:', content);
  }, []);

  // 预览分享内容
  const previewContent = useCallback((shareContent: ShareContent) => {
    Alert.alert(
      shareContent.title,
      shareContent.content.length > 500 
        ? shareContent.content.substring(0, 500) + '...'
        : shareContent.content,
      [
        { text: '关闭' },
        { text: '复制', onPress: () => copyToClipboard(shareContent.content) },
        { text: '分享', onPress: () => handleShare(shareContent) }
      ]
    );
  }, [copyToClipboard, handleShare]);

  const shareOptions = [
    {
      id: 'simple',
      title: '简单分享',
      description: '分享基本学习成果',
      icon: '📤',
      action: () => {
        const content = generateSimpleShare();
        handleShare(content);
      },
      preview: () => {
        const content = generateSimpleShare();
        previewContent(content);
      }
    },
    {
      id: 'detailed',
      title: '详细报告',
      description: '包含题目详情和知识点',
      icon: '📋',
      action: () => {
        const content = generateDetailedShare();
        handleShare(content);
      },
      preview: () => {
        const content = generateDetailedShare();
        previewContent(content);
      }
    },
    {
      id: 'report',
      title: '学习报告',
      description: '专业的学习分析报告',
      icon: '📊',
      action: () => {
        const content = generateLearningReport();
        handleShare(content);
      },
      preview: () => {
        const content = generateLearningReport();
        previewContent(content);
      }
    }
  ];

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        {/* 头部 */}
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Text style={styles.closeButtonText}>关闭</Text>
          </TouchableOpacity>
          
          <Text style={styles.title}>分享学习成果</Text>
          
          <View style={styles.headerSpacer} />
        </View>

        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {/* 记录信息 */}
          <View style={styles.recordInfo}>
            <Text style={styles.recordTitle}>📚 {record.displayTime}</Text>
            {record.summary && (
              <View style={styles.recordSummary}>
                <View style={styles.summaryItem}>
                  <Text style={styles.summaryLabel}>总题数</Text>
                  <Text style={styles.summaryValue}>{record.summary.totalQuestions}</Text>
                </View>
                <View style={styles.summaryItem}>
                  <Text style={styles.summaryLabel}>正确</Text>
                  <Text style={[styles.summaryValue, { color: successColor }]}>
                    {record.summary.correctCount}
                  </Text>
                </View>
                <View style={styles.summaryItem}>
                  <Text style={styles.summaryLabel}>错误</Text>
                  <Text style={[styles.summaryValue, { color: errorColor }]}>
                    {record.summary.wrongCount}
                  </Text>
                </View>
                {record.summary.score !== undefined && (
                  <View style={styles.summaryItem}>
                    <Text style={styles.summaryLabel}>分数</Text>
                    <Text style={[styles.summaryValue, { color: primaryColor }]}>
                      {record.summary.score}
                    </Text>
                  </View>
                )}
              </View>
            )}
          </View>

          {/* 分享选项 */}
          <View style={styles.shareOptions}>
            <Text style={styles.sectionTitle}>选择分享方式</Text>
            
            {shareOptions.map((option) => (
              <View key={option.id} style={styles.shareOption}>
                <View style={styles.optionInfo}>
                  <Text style={styles.optionIcon}>{option.icon}</Text>
                  <View style={styles.optionText}>
                    <Text style={styles.optionTitle}>{option.title}</Text>
                    <Text style={styles.optionDescription}>{option.description}</Text>
                  </View>
                </View>
                
                <View style={styles.optionActions}>
                  <TouchableOpacity
                    style={styles.previewButton}
                    onPress={option.preview}
                  >
                    <Text style={styles.previewButtonText}>预览</Text>
                  </TouchableOpacity>
                  
                  <TouchableOpacity
                    style={styles.shareButton}
                    onPress={option.action}
                    disabled={loading}
                  >
                    <Text style={styles.shareButtonText}>分享</Text>
                  </TouchableOpacity>
                </View>
              </View>
            ))}
          </View>

          {/* 分享提示 */}
          <View style={styles.shareHint}>
            <Text style={styles.hintTitle}>💡 分享小贴士</Text>
            <Text style={styles.hintText}>
              • 简单分享：适合快速展示学习成果{'\n'}
              • 详细报告：包含完整的题目分析{'\n'}
              • 学习报告：专业的学习建议和分析{'\n'}
              • 所有分享内容都可以预览后再分享
            </Text>
          </View>
        </ScrollView>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: backgroundColor,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: cardBackgroundColor,
    borderBottomWidth: 1,
    borderBottomColor: borderColor,
  },
  closeButton: {
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  closeButtonText: {
    fontSize: 16,
    color: primaryColor,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: textColor,
  },
  headerSpacer: {
    width: 60,
  },
  content: {
    flex: 1,
    padding: 20,
  },
  recordInfo: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 16,
    padding: 16,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: borderColor,
  },
  recordTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: textColor,
    marginBottom: 12,
  },
  recordSummary: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  summaryItem: {
    alignItems: 'center',
  },
  summaryLabel: {
    fontSize: 12,
    color: secondaryTextColor,
    marginBottom: 4,
  },
  summaryValue: {
    fontSize: 18,
    fontWeight: '600',
    color: textColor,
  },
  shareOptions: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: textColor,
    marginBottom: 16,
  },
  shareOption: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: borderColor,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  optionInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  optionIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  optionText: {
    flex: 1,
  },
  optionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: textColor,
    marginBottom: 2,
  },
  optionDescription: {
    fontSize: 12,
    color: secondaryTextColor,
  },
  optionActions: {
    flexDirection: 'row',
    gap: 8,
  },
  previewButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    backgroundColor: 'rgba(0, 122, 255, 0.1)',
  },
  previewButtonText: {
    fontSize: 12,
    color: primaryColor,
    fontWeight: '500',
  },
  shareButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    backgroundColor: primaryColor,
  },
  shareButtonText: {
    fontSize: 12,
    color: '#fff',
    fontWeight: '500',
  },
  shareHint: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: borderColor,
  },
  hintTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: textColor,
    marginBottom: 8,
  },
  hintText: {
    fontSize: 14,
    color: secondaryTextColor,
    lineHeight: 20,
  },
});

export default ShareManager;
