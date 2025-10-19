/**
 * 生成试卷界面
 * 允许用户从历史记录中生成PDF格式的练习试卷
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  ScrollView,
  StatusBar,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/NavigationTypes';
import paperService, { PaperStatistics, PaperPreview } from '../services/paperService';
import {
  primaryColor,
  textPrimary,
  textSecondary,
  backgroundPrimary,
  cardBackground,
  borderColor,
  successColor,
  errorColor,
  warningColor,
  primaryAlpha10,
  successAlpha10,
  errorAlpha10,
} from '../styles/colors';
import { typography, spacing, borderRadius, shadows } from '../styles/designSystem';

const GeneratePaperScreen: React.FC = () => {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();

  // 状态管理
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [statistics, setStatistics] = useState<PaperStatistics | null>(null);
  const [preview, setPreview] = useState<PaperPreview | null>(null);
  const [selectedCount, setSelectedCount] = useState(10);

  // 加载统计信息
  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      setLoading(true);
      const stats = await paperService.getStatistics();
      setStatistics(stats);
      
      if (stats.can_generate) {
        console.log('✅ 可以生成试卷');
      } else {
        console.log('⚠️ 题目不足，无法生成试卷');
      }
    } catch (error: any) {
      console.error('❌ 加载统计信息失败:', error);
      Alert.alert('加载失败', error.message || '无法加载题目信息');
    } finally {
      setLoading(false);
    }
  };

  // 预览试卷
  const handlePreview = async () => {
    try {
      setLoading(true);
      const previewData = await paperService.previewPaper({
        maxQuestions: selectedCount,
      });
      setPreview(previewData);
      
      Alert.alert(
        '预览结果',
        previewData.message,
        [{ text: '确定' }]
      );
    } catch (error: any) {
      console.error('❌ 预览失败:', error);
      Alert.alert('预览失败', error.message || '无法预览试卷');
    } finally {
      setLoading(false);
    }
  };

  // 生成并下载试卷
  const handleGenerate = async () => {
    if (!statistics?.can_generate) {
      Alert.alert('无法生成', '没有足够的题目，请先完成作业批改');
      return;
    }

    Alert.alert(
      '确认生成',
      `将生成包含${Math.min(selectedCount, statistics.total_similar_questions)}道题目的PDF试卷`,
      [
        { text: '取消', style: 'cancel' },
        {
          text: '确认',
          onPress: async () => {
            try {
              setGenerating(true);
              
              const filePath = await paperService.generateAndDownloadPaper({
                maxQuestions: selectedCount,
                title: '练习试卷',
              });

              Alert.alert(
                '生成成功',
                'PDF试卷已生成并保存到您的设备',
                [
                  { text: '确定' }
                ]
              );

            } catch (error: any) {
              console.error('❌ 生成失败:', error);
              Alert.alert(
                '生成失败',
                error.message || '无法生成试卷，请稍后重试'
              );
            } finally {
              setGenerating(false);
            }
          },
        },
      ]
    );
  };

  // 选择题目数量
  const renderQuestionCountSelector = () => {
    const counts = [5, 10, 15, 20];
    const maxAvailable = statistics?.total_similar_questions || 0;

    return (
      <View style={styles.selectorContainer}>
        <Text style={styles.selectorLabel}>选择题目数量：</Text>
        <View style={styles.countButtons}>
          {counts.map((count) => {
            const isDisabled = count > maxAvailable;
            const isSelected = count === selectedCount;

            return (
              <TouchableOpacity
                key={count}
                style={[
                  styles.countButton,
                  isSelected && styles.countButtonSelected,
                  isDisabled && styles.countButtonDisabled,
                ]}
                onPress={() => !isDisabled && setSelectedCount(count)}
                disabled={isDisabled}
              >
                <Text
                  style={[
                    styles.countButtonText,
                    isSelected && styles.countButtonTextSelected,
                    isDisabled && styles.countButtonTextDisabled,
                  ]}
                >
                  {count}题
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>
    );
  };

  // 渲染统计信息
  const renderStatistics = () => {
    if (!statistics) return null;

    return (
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{statistics.total_records}</Text>
          <Text style={styles.statLabel}>历史记录</Text>
        </View>
        
        <View style={styles.statCard}>
          <Text style={[styles.statValue, { color: successColor }]}>
            {statistics.total_similar_questions}
          </Text>
          <Text style={styles.statLabel}>可用题目</Text>
        </View>
        
        <View style={styles.statCard}>
          <Text style={[styles.statValue, { color: primaryColor }]}>
            {statistics.recommended_count}
          </Text>
          <Text style={styles.statLabel}>推荐数量</Text>
        </View>
      </View>
    );
  };

  // 加载中界面
  if (loading && !statistics) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="dark-content" />
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={primaryColor} />
          <Text style={styles.loadingText}>加载中...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />
      
      {/* 标题栏 */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>← 返回</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>生成试卷</Text>
        <View style={styles.backButton} />
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {/* 说明卡片 */}
        <View style={styles.infoCard}>
          <Text style={styles.infoIcon}>📝</Text>
          <Text style={styles.infoTitle}>智能生成练习试卷</Text>
          <Text style={styles.infoText}>
            从您的历史批改记录中自动提取相似题目，生成PDF格式的练习试卷，方便打印和练习。
          </Text>
        </View>

        {/* 统计信息 */}
        {renderStatistics()}

        {/* 题目数量选择器 */}
        {renderQuestionCountSelector()}

        {/* 状态提示 */}
        {statistics && !statistics.can_generate && (
          <View style={styles.warningCard}>
            <Text style={styles.warningIcon}>⚠️</Text>
            <Text style={styles.warningText}>
              题目数量不足，请先完成作业批改以积累更多练习题。
            </Text>
          </View>
        )}

        {/* 操作按钮 */}
        <View style={styles.actionButtons}>
          {/* 预览按钮 */}
          <TouchableOpacity
            style={[styles.button, styles.previewButton]}
            onPress={handlePreview}
            disabled={loading || !statistics?.can_generate}
          >
            <Text style={styles.previewButtonText}>
              {loading ? '加载中...' : '预览题目'}
            </Text>
          </TouchableOpacity>

          {/* 生成按钮 */}
          <TouchableOpacity
            style={[
              styles.button,
              styles.generateButton,
              (!statistics?.can_generate || generating) && styles.buttonDisabled,
            ]}
            onPress={handleGenerate}
            disabled={!statistics?.can_generate || generating}
          >
            {generating ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <Text style={styles.generateButtonText}>
                生成PDF试卷
              </Text>
            )}
          </TouchableOpacity>
        </View>

        {/* 预览内容 */}
        {preview && preview.questions.length > 0 && (
          <View style={styles.previewContainer}>
            <Text style={styles.previewTitle}>题目预览</Text>
            <Text style={styles.previewSubtitle}>
              共找到 {preview.total_found} 道题目，将使用 {preview.will_use} 道
            </Text>
            
            {preview.questions.slice(0, 3).map((q, index) => (
              <View key={index} style={styles.previewQuestion}>
                <Text style={styles.previewQuestionNumber}>{index + 1}.</Text>
                <Text style={styles.previewQuestionText}>
                  {q.question || q.similar_question || q.content || '题目内容'}
                </Text>
              </View>
            ))}
            
            {preview.questions.length > 3 && (
              <Text style={styles.previewMore}>
                ...还有 {preview.questions.length - 3} 道题目
              </Text>
            )}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: backgroundPrimary,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: spacing.md,
    ...typography.bodyMedium,
    color: textSecondary,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: borderColor,
    backgroundColor: '#FFFFFF',
  },
  backButton: {
    padding: spacing.sm,
    width: 60,
  },
  backButtonText: {
    ...typography.bodyMedium,
    color: primaryColor,
  },
  headerTitle: {
    ...typography.heading2,
    color: textPrimary,
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: spacing.lg,
  },
  infoCard: {
    backgroundColor: primaryAlpha10,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    alignItems: 'center',
  },
  infoIcon: {
    fontSize: 48,
    marginBottom: spacing.sm,
  },
  infoTitle: {
    ...typography.heading3,
    color: textPrimary,
    marginBottom: spacing.sm,
  },
  infoText: {
    ...typography.bodyMedium,
    color: textSecondary,
    textAlign: 'center',
    lineHeight: 22,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.lg,
  },
  statCard: {
    flex: 1,
    backgroundColor: cardBackground,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    marginHorizontal: spacing.xs,
    alignItems: 'center',
    ...shadows.level1,
  },
  statValue: {
    ...typography.heading2,
    color: primaryColor,
    marginBottom: spacing.xs,
  },
  statLabel: {
    ...typography.caption,
    color: textSecondary,
  },
  selectorContainer: {
    marginBottom: spacing.lg,
  },
  selectorLabel: {
    ...typography.bodyMedium,
    fontWeight: '600',
    color: textPrimary,
    marginBottom: spacing.sm,
  },
  countButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  countButton: {
    flex: 1,
    paddingVertical: spacing.md,
    marginHorizontal: spacing.xs,
    backgroundColor: cardBackground,
    borderRadius: borderRadius.md,
    borderWidth: 2,
    borderColor: borderColor,
    alignItems: 'center',
  },
  countButtonSelected: {
    backgroundColor: primaryAlpha10,
    borderColor: primaryColor,
  },
  countButtonDisabled: {
    opacity: 0.4,
  },
  countButtonText: {
    ...typography.bodyMedium,
    color: textSecondary,
  },
  countButtonTextSelected: {
    ...typography.bodyMedium,
    fontWeight: '600',
    color: primaryColor,
  },
  countButtonTextDisabled: {
    color: textSecondary,
  },
  warningCard: {
    backgroundColor: errorAlpha10,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  warningIcon: {
    fontSize: 24,
    marginRight: spacing.sm,
  },
  warningText: {
    flex: 1,
    ...typography.bodyMedium,
    color: errorColor,
  },
  actionButtons: {
    marginBottom: spacing.lg,
  },
  button: {
    paddingVertical: spacing.md,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    marginBottom: spacing.sm,
    ...shadows.level2,
  },
  previewButton: {
    backgroundColor: '#FFFFFF',
    borderWidth: 2,
    borderColor: primaryColor,
  },
  previewButtonText: {
    ...typography.buttonMedium,
    color: primaryColor,
  },
  generateButton: {
    backgroundColor: primaryColor,
  },
  generateButtonText: {
    ...typography.buttonMedium,
    color: '#FFFFFF',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  previewContainer: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    ...shadows.level1,
  },
  previewTitle: {
    ...typography.heading3,
    color: textPrimary,
    marginBottom: spacing.xs,
  },
  previewSubtitle: {
    ...typography.caption,
    color: textSecondary,
    marginBottom: spacing.md,
  },
  previewQuestion: {
    flexDirection: 'row',
    marginBottom: spacing.sm,
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: borderColor,
  },
  previewQuestionNumber: {
    ...typography.bodyMedium,
    fontWeight: '600',
    color: primaryColor,
    marginRight: spacing.sm,
    minWidth: 30,
  },
  previewQuestionText: {
    flex: 1,
    ...typography.bodyMedium,
    color: textPrimary,
    lineHeight: 22,
  },
  previewMore: {
    ...typography.caption,
    color: textSecondary,
    textAlign: 'center',
    marginTop: spacing.sm,
    fontStyle: 'italic',
  },
});

export default GeneratePaperScreen;

