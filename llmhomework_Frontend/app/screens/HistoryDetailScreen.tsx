import { RouteProp, useRoute, useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView, 
  ScrollView,
  TouchableOpacity,
  Alert,
  StatusBar,
  ActivityIndicator,
  Image
} from 'react-native';
import { RootStackParamList } from '../navigation/NavigationTypes';
import { HistoryRecord } from '../types/HistoryTypes';
import historyService from '../services/historyService';
import ShareManager from '../components/ShareManager';
import { 
  primaryColor, 
  textColor, 
  secondaryTextColor, 
  backgroundColor, 
  cardBackgroundColor,
  borderColor,
  errorColor
} from '../styles/colors';

type HistoryDetailRouteProp = RouteProp<RootStackParamList, 'HistoryDetail'>;

const HistoryDetailScreen: React.FC = () => {
  const route = useRoute<HistoryDetailRouteProp>();
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  
  const { recordId } = route.params;
  
  const [record, setRecord] = useState<HistoryRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [showShareManager, setShowShareManager] = useState(false);

  // 加载历史记录详情
  useEffect(() => {
    const loadRecord = async () => {
      try {
        const recordData = await historyService.getRecordById(recordId);
        if (recordData) {
          setRecord(recordData);
          console.log(`📄 加载历史详情: ${recordData.displayTime}`);
        } else {
          Alert.alert('记录不存在', '该历史记录可能已被删除', [
            { text: '确定', onPress: () => navigation.goBack() }
          ]);
        }
      } catch (error) {
        console.error('加载历史详情失败:', error);
        Alert.alert('加载失败', '无法加载历史记录详情', [
          { text: '确定', onPress: () => navigation.goBack() }
        ]);
      } finally {
        setLoading(false);
      }
    };

    loadRecord();
  }, [recordId, navigation]);

  // 删除当前记录
  const deleteCurrentRecord = async () => {
    if (!record) return;

    Alert.alert(
      '确认删除',
      `确定要删除 ${record.displayTime} 的批改记录吗？`,
      [
        { text: '取消', style: 'cancel' },
        {
          text: '删除',
          style: 'destructive',
          onPress: async () => {
            try {
              const success = await historyService.deleteRecord(record.id);
              if (success) {
                Alert.alert('删除成功', '历史记录已删除', [
                  { text: '确定', onPress: () => navigation.goBack() }
                ]);
              } else {
                Alert.alert('删除失败', '删除操作失败，请重试');
              }
            } catch (error) {
              console.error('删除记录失败:', error);
              Alert.alert('删除失败', '删除操作失败，请重试');
            }
          }
        }
      ]
    );
  };

  // 重新批改（复用这次的结果）
  const viewInResultScreen = () => {
    if (!record) return;

    navigation.navigate('Result', {
      gradingResult: record.gradingResult,
      wrongKnowledges: record.wrongKnowledges || [],
      taskId: record.taskId,
      timestamp: record.timestamp,
    });
  };

  // 复制任务ID
  const copyTaskId = () => {
    if (!record) return;
    // 在实际项目中，这里可以使用 Clipboard API
    Alert.alert('复制成功', `任务ID: ${record.taskId} 已复制到剪贴板`);
  };

  // 打开分享管理器
  const openShareManager = () => {
    if (!record) return;
    setShowShareManager(true);
  };

  // 查看知识点分析
  const viewKnowledgePoints = () => {
    if (!record) return;

    navigation.navigate('KnowledgePoints', {
      knowledgePoints: [],
      wrongKnowledges: record.wrongKnowledges,
      gradingResult: gradingResults,
    });
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={primaryColor} />
          <Text style={styles.loadingText}>加载中...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!record) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>记录不存在</Text>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Text style={styles.backButtonText}>返回</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const gradingResults = record.gradingResult?.grading_result || [];

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor={backgroundColor} />
      
      {/* 顶部导航栏 */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.headerBackButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.headerBackText}>← 返回</Text>
        </TouchableOpacity>
        
        <Text style={styles.headerTitle}>批改详情</Text>
        
        <TouchableOpacity 
          style={styles.deleteButton}
          onPress={deleteCurrentRecord}
        >
          <Text style={styles.deleteButtonText}>删除</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.container} showsVerticalScrollIndicator={true}>
        {/* 记录信息卡片 */}
        <View style={styles.infoCard}>
          <View style={styles.infoHeader}>
            <Text style={styles.infoTitle}>📚 批改记录</Text>
            <Text style={styles.timeText}>{record.displayTime}</Text>
          </View>
          
          <View style={styles.infoContent}>
            <View style={styles.imageSection}>
              <Text style={styles.sectionLabel}>原始图片</Text>
              <Image source={{ uri: record.imageUri }} style={styles.originalImage} />
            </View>
            
            <View style={styles.summarySection}>
              <Text style={styles.sectionLabel}>批改摘要</Text>
              {record.summary && (
                <View style={styles.summaryStats}>
                  <View style={styles.summaryItem}>
                    <Text style={styles.summaryValue}>{record.summary.totalQuestions}</Text>
                    <Text style={styles.summaryLabel}>总题数</Text>
                  </View>
                  <View style={styles.summaryItem}>
                    <Text style={[styles.summaryValue, { color: '#34C759' }]}>{record.summary.correctCount}</Text>
                    <Text style={styles.summaryLabel}>正确</Text>
                  </View>
                  <View style={styles.summaryItem}>
                    <Text style={[styles.summaryValue, { color: errorColor }]}>{record.summary.wrongCount}</Text>
                    <Text style={styles.summaryLabel}>错误</Text>
                  </View>
                </View>
              )}
              
              <Text style={styles.taskIdText}>任务ID: {record.taskId}</Text>
            </View>
          </View>

          {/* 操作按钮 */}
          <View style={styles.actionButtons}>
            <TouchableOpacity 
              style={[styles.actionButton, styles.primaryAction]}
              onPress={viewInResultScreen}
            >
              <Text style={styles.actionButtonText}>📊 查看结果</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={[styles.actionButton, styles.secondaryAction]}
              onPress={openShareManager}
            >
              <Text style={[styles.actionButtonText, styles.secondaryActionText]}>📤 分享</Text>
            </TouchableOpacity>
          </View>

          {/* 更多操作 */}
          <View style={styles.moreActions}>
            <TouchableOpacity 
              style={styles.moreActionItem}
              onPress={copyTaskId}
            >
              <Text style={styles.moreActionIcon}>📋</Text>
              <Text style={styles.moreActionText}>复制任务ID</Text>
            </TouchableOpacity>
            
            {record.wrongKnowledges && record.wrongKnowledges.length > 0 && (
              <TouchableOpacity 
                style={styles.moreActionItem}
                onPress={viewKnowledgePoints}
              >
                <Text style={styles.moreActionIcon}>🧠</Text>
                <Text style={styles.moreActionText}>知识点分析</Text>
              </TouchableOpacity>
            )}
          </View>
        </View>


      </ScrollView>

      {/* 分享管理器 */}
      {record && (
        <ShareManager
          visible={showShareManager}
          onClose={() => setShowShareManager(false)}
          record={record}
        />
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
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
  headerBackButton: {
    flex: 1,
  },
  headerBackText: {
    fontSize: 16,
    color: primaryColor,
    fontWeight: '500',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: textColor,
    textAlign: 'center',
  },
  deleteButton: {
    flex: 1,
    alignItems: 'flex-end',
  },
  deleteButtonText: {
    fontSize: 14,
    color: errorColor,
    fontWeight: '500',
  },
  container: {
    flex: 1,
    padding: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: secondaryTextColor,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  errorText: {
    fontSize: 18,
    color: errorColor,
    marginBottom: 20,
    textAlign: 'center',
  },
  backButton: {
    backgroundColor: primaryColor,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  backButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '500',
  },
  infoCard: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: borderColor,
  },
  infoHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: textColor,
  },
  timeText: {
    fontSize: 14,
    color: secondaryTextColor,
  },
  infoContent: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  imageSection: {
    marginRight: 16,
  },
  sectionLabel: {
    fontSize: 12,
    color: secondaryTextColor,
    marginBottom: 8,
    fontWeight: '500',
  },
  originalImage: {
    width: 80,
    height: 80,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
  },
  summarySection: {
    flex: 1,
  },
  summaryStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 12,
  },
  summaryItem: {
    alignItems: 'center',
  },
  summaryValue: {
    fontSize: 18,
    fontWeight: '600',
    color: textColor,
  },
  summaryLabel: {
    fontSize: 12,
    color: secondaryTextColor,
    marginTop: 2,
  },
  taskIdText: {
    fontSize: 12,
    color: secondaryTextColor,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
  },
  actionButton: {
    flex: 1,
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  primaryAction: {
    backgroundColor: primaryColor,
  },
  secondaryAction: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: primaryColor,
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
  secondaryActionText: {
    color: primaryColor,
  },
  moreActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: borderColor,
  },
  moreActionItem: {
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  moreActionIcon: {
    fontSize: 18,
    marginBottom: 4,
  },
  moreActionText: {
    fontSize: 12,
    color: secondaryTextColor,
    fontWeight: '500',
  },
  resultsSection: {
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: textColor,
    marginBottom: 12,
  },
  noResultsCard: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: borderColor,
  },
  noResultsText: {
    fontSize: 14,
    color: secondaryTextColor,
  },
});

export default HistoryDetailScreen;
