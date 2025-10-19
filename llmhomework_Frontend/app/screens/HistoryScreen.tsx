import { useNavigation, useFocusEffect } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useState, useCallback } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView, 
  FlatList,
  TouchableOpacity,
  Alert,
  RefreshControl,
  StatusBar,
  Image,
  TextInput,
  Keyboard
} from 'react-native';
import { DecorativeButton } from '../components/DecorativeButton';
import { RootStackParamList } from '../navigation/NavigationTypes';
import { HistoryRecord, HistoryFilters } from '../types/HistoryTypes';
import historyService from '../services/historyService';
import AdvancedFilter from '../components/AdvancedFilter';
import LearningAnalytics from '../components/LearningAnalytics';
import DataManager from '../components/DataManager';
import LearningInsights from '../components/LearningInsights';
import {
  primaryColor,
  textPrimary,
  textSecondary,
  backgroundPrimary,
  cardBackground,
  borderColor,
  errorColor,
  successColor,
  primaryAlpha10,
  errorAlpha10,
  successAlpha10
} from '../styles/colors';
import { typography, spacing, borderRadius, shadows } from '../styles/designSystem';

const HistoryScreen: React.FC = () => {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  
  const [historyRecords, setHistoryRecords] = useState<HistoryRecord[]>([]);
  const [filteredRecords, setFilteredRecords] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [showSearch, setShowSearch] = useState(false);
  const [statistics, setStatistics] = useState<any>(null);
  const [batchMode, setBatchMode] = useState(false);
  const [selectedRecords, setSelectedRecords] = useState<Set<string>>(new Set());
  const [showAdvancedFilter, setShowAdvancedFilter] = useState(false);
  const [activeFilters, setActiveFilters] = useState<HistoryFilters>({});
  const [usingAdvancedFilter, setUsingAdvancedFilter] = useState(false);
  const [showDataManager, setShowDataManager] = useState(false);

  // 加载历史记录
  const loadHistory = useCallback(async () => {
    try {
      const records = await historyService.getHistory();
      const stats = await historyService.getHistoryStats();
      setHistoryRecords(records);
      setFilteredRecords(records); // 初始时显示所有记录
      setStatistics(stats);
      console.log(`📚 加载了 ${records.length} 条历史记录`);
      console.log(`📊 统计信息:`, stats);
    } catch (error) {
      console.error('加载历史记录失败:', error);
      Alert.alert('加载失败', '无法加载历史记录，请重试');
      } finally {
        setLoading(false);
      setRefreshing(false);
      }
  }, []);

  // 页面聚焦时刷新数据
  useFocusEffect(
    useCallback(() => {
      loadHistory();
    }, [loadHistory])
  );

  // 下拉刷新
  const onRefresh = useCallback(() => {
    setRefreshing(true);
    loadHistory();
  }, [loadHistory]);

  // 搜索过滤
  const filterRecords = useCallback((text: string) => {
    if (!text.trim()) {
      setFilteredRecords(historyRecords);
      return;
    }

    const filtered = historyRecords.filter(record => {
      const searchLower = text.toLowerCase();
      return (
        record.displayTime.toLowerCase().includes(searchLower) ||
        record.taskId.toLowerCase().includes(searchLower) ||
        (record.summary && record.summary.totalQuestions.toString().includes(searchLower))
      );
    });

    setFilteredRecords(filtered);
    console.log(`🔍 搜索 "${text}" 找到 ${filtered.length} 条记录`);
  }, [historyRecords]);

  // 处理搜索文本变化
  const handleSearchChange = useCallback((text: string) => {
    setSearchText(text);
    filterRecords(text);
  }, [filterRecords]);

  // 清除搜索
  const clearSearch = useCallback(() => {
    setSearchText('');
    setShowSearch(false);
    setFilteredRecords(historyRecords);
    Keyboard.dismiss();
  }, [historyRecords]);

  // 进入/退出批量模式
  const toggleBatchMode = useCallback(() => {
    setBatchMode(!batchMode);
    setSelectedRecords(new Set());
  }, [batchMode]);

  // 选择/取消选择记录
  const toggleSelectRecord = useCallback((recordId: string) => {
    setSelectedRecords(prev => {
      const newSet = new Set(prev);
      if (newSet.has(recordId)) {
        newSet.delete(recordId);
      } else {
        newSet.add(recordId);
      }
      return newSet;
    });
  }, []);

  // 全选/取消全选
  const toggleSelectAll = useCallback(() => {
    if (selectedRecords.size === filteredRecords.length) {
      setSelectedRecords(new Set());
    } else {
      setSelectedRecords(new Set(filteredRecords.map(record => record.id)));
    }
  }, [selectedRecords.size, filteredRecords]);

  // 批量删除选中的记录
  const batchDeleteRecords = useCallback(async () => {
    if (selectedRecords.size === 0) {
      Alert.alert('提示', '请先选择要删除的记录');
      return;
    }

    Alert.alert(
      '确认删除',
      `确定要删除选中的 ${selectedRecords.size} 条记录吗？此操作不可恢复。`,
      [
        { text: '取消', style: 'cancel' },
        {
          text: '删除',
          style: 'destructive',
          onPress: async () => {
            try {
              let successCount = 0;
              for (const recordId of selectedRecords) {
                const success = await historyService.deleteRecord(recordId);
                if (success) successCount++;
              }
              
              await loadHistory();
              setBatchMode(false);
              setSelectedRecords(new Set());
              
              Alert.alert('删除完成', `成功删除 ${successCount} 条记录`);
            } catch (error) {
              console.error('批量删除失败:', error);
              Alert.alert('删除失败', '批量删除操作失败，请重试');
            }
          }
        }
      ]
    );
  }, [selectedRecords, loadHistory]);

  // 应用高级筛选
  const applyAdvancedFilters = useCallback(async (filters: HistoryFilters) => {
    try {
      setActiveFilters(filters);
      const hasFilters = Object.keys(filters).length > 0;
      setUsingAdvancedFilter(hasFilters);
      
      if (hasFilters) {
        console.log('🔍 应用高级筛选:', filters);
        const filtered = await historyService.getFilteredHistory(filters);
        setFilteredRecords(filtered);
        console.log(`✅ 筛选结果: ${filtered.length} 条记录`);
      } else {
        // 没有筛选条件，显示所有记录
        setFilteredRecords(historyRecords);
      }
    } catch (error) {
      console.error('应用高级筛选失败:', error);
      Alert.alert('筛选失败', '应用筛选条件时出错，请重试');
    }
  }, [historyRecords]);

  // 清除高级筛选
  const clearAdvancedFilters = useCallback(() => {
    setActiveFilters({});
    setUsingAdvancedFilter(false);
    setFilteredRecords(historyRecords);
  }, [historyRecords]);

  // 修复历史数据
  const fixHistoryData = useCallback(async () => {
    Alert.alert(
      '修复历史数据',
      '检测到可能存在数据统计错误，是否要修复现有的历史记录？\n\n这将重新计算所有记录的正确率和统计信息。',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '修复',
          onPress: async () => {
            try {
              setLoading(true);
              const result = await historyService.fixExistingRecords();
              
              if (result.fixed > 0) {
                Alert.alert(
                  '修复完成',
                  `已成功修复 ${result.fixed} 条记录的统计数据！\n\n现在刷新页面查看修复结果。`,
                  [
                    {
                      text: '确定',
                      onPress: () => {
                        loadHistory(); // 重新加载数据
                      }
                    }
                  ]
                );
              } else {
                Alert.alert('修复完成', '没有发现需要修复的记录。');
              }

              if (result.errors.length > 0) {
                console.error('修复过程中的错误:', result.errors);
              }
            } catch (error) {
              console.error('修复失败:', error);
              Alert.alert('修复失败', `修复过程中出现错误: ${error}`);
            } finally {
              setLoading(false);
            }
          }
        }
      ]
    );
  }, [loadHistory]);

  // 删除单条记录
  const deleteRecord = useCallback(async (record: HistoryRecord) => {
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
                await loadHistory(); // 重新加载列表
                Alert.alert('删除成功', '历史记录已删除');
              } else {
                Alert.alert('删除失败', '未找到该记录');
              }
            } catch (error) {
              console.error('删除记录失败:', error);
              Alert.alert('删除失败', '删除操作失败，请重试');
            }
          }
        }
      ]
    );
  }, [loadHistory]);

  // 清空所有历史记录
  const clearAllHistory = useCallback(() => {
    if (historyRecords.length === 0) {
      Alert.alert('提示', '没有历史记录可以清空');
      return;
    }

    Alert.alert(
      '确认清空',
      `确定要清空所有 ${historyRecords.length} 条历史记录吗？此操作不可恢复。`,
      [
        { text: '取消', style: 'cancel' },
        {
          text: '清空',
          style: 'destructive',
          onPress: async () => {
            try {
              const success = await historyService.clearAllHistory();
              if (success) {
                await loadHistory();
                clearSearch(); // 清除搜索状态
                Alert.alert('清空成功', '所有历史记录已清空');
              } else {
                Alert.alert('清空失败', '清空操作失败，请重试');
              }
            } catch (error) {
              console.error('清空历史记录失败:', error);
              Alert.alert('清空失败', '清空操作失败，请重试');
            }
          }
        }
      ]
    );
  }, [historyRecords.length, loadHistory, clearSearch]);

  // 跳转到历史详情
  const navigateToDetail = useCallback((record: HistoryRecord) => {
    navigation.navigate('HistoryDetail', { recordId: record.id });
  }, [navigation]);

  // 渲染历史记录项
  const renderHistoryItem = useCallback(({ item }: { item: HistoryRecord }) => {
    const summary = item.summary || { totalQuestions: 0, correctCount: 0, wrongCount: 0 };
    const isSelected = selectedRecords.has(item.id);
    
    const handlePress = () => {
      if (batchMode) {
        toggleSelectRecord(item.id);
      } else {
        navigateToDetail(item);
      }
    };
    
    return (
      <TouchableOpacity 
        style={[
          styles.historyItem,
          batchMode && styles.historyItemBatch,
          isSelected && styles.historyItemSelected
        ]}
        onPress={handlePress}
        activeOpacity={0.7}
      >
        <View style={styles.itemHeader}>
          {batchMode && (
            <View style={styles.checkboxContainer}>
              <View style={[styles.checkbox, isSelected && styles.checkboxSelected]}>
                {isSelected && <Text style={styles.checkmark}>✓</Text>}
              </View>
            </View>
          )}
          <View style={styles.timeContainer}>
            <Text style={styles.timeIcon}>📚</Text>
            <Text style={styles.timeText}>{item.displayTime}</Text>
          </View>
          {!batchMode && (
            <TouchableOpacity
              style={styles.deleteButton}
              onPress={() => deleteRecord(item)}
              hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
            >
              <Text style={styles.deleteButtonText}>删除</Text>
            </TouchableOpacity>
          )}
        </View>
        
        <View style={styles.itemContent}>
          <View style={styles.imagePreview}>
            <Image source={{ uri: item.imageUri }} style={styles.thumbnailImage} />
          </View>
          
          <View style={styles.summaryContainer}>
            <Text style={styles.summaryTitle}>批改结果摘要</Text>
            <View style={styles.statsRow}>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{summary.totalQuestions}</Text>
                <Text style={styles.statLabel}>总题数</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={[styles.statValue, { color: successColor }]}>{summary.correctCount}</Text>
                <Text style={styles.statLabel}>正确</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={[styles.statValue, { color: errorColor }]}>{summary.wrongCount}</Text>
                <Text style={styles.statLabel}>错误</Text>
              </View>
            </View>
          </View>
        </View>
        
        <View style={styles.itemFooter}>
          <Text style={styles.taskId}>任务ID: {item.taskId}</Text>
          <Text style={styles.viewDetail}>点击查看详情 →</Text>
      </View>
      </TouchableOpacity>
    );
  }, [batchMode, selectedRecords, navigateToDetail, deleteRecord, toggleSelectRecord]);

  // 空状态组件
  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Text style={styles.emptyIcon}>📚</Text>
      <Text style={styles.emptyTitle}>暂无历史记录</Text>
      <Text style={styles.emptyDescription}>完成题目批改后，记录会自动保存在这里</Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor={backgroundPrimary} />
      
      {/* 顶部导航栏 */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <TouchableOpacity 
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.backButtonText}>← 返回</Text>
          </TouchableOpacity>
        </View>
        
        <Text style={styles.headerTitle}>历史记录</Text>
        
        <View style={styles.headerRight}>
          {/* 只保留搜索和取消按钮 */}
          {showSearch && (
            <TouchableOpacity 
              style={styles.cancelSearchButton}
              onPress={clearSearch}
            >
              <Text style={styles.cancelSearchText}>取消</Text>
            </TouchableOpacity>
          )}
          {batchMode && (
            <TouchableOpacity 
              style={styles.cancelSearchButton}
              onPress={toggleBatchMode}
            >
              <Text style={styles.cancelSearchText}>取消</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* 功能工具栏 */}
      {historyRecords.length > 0 && !showSearch && !batchMode && (
        <View style={styles.toolBar}>
          <View style={styles.decorativeButtonWrapper}>
            <DecorativeButton
              onPress={() => setShowSearch(true)}
              iconName="search"
              size="sm"
              gradientColors={['#007AFF', '#5856D6']}
              outerColor="#BF5AF2"
              borderColor="#8E44AD"
            />
            <Text style={styles.toolButtonLabel}>🔍 搜索</Text>
          </View>
          
          <View style={styles.decorativeButtonWrapper}>
            <DecorativeButton
              onPress={() => setShowAdvancedFilter(true)}
              iconName="filter"
              size="sm"
              gradientColors={usingAdvancedFilter ? ['#32D74B', '#30D158'] : ['#8E8E93', '#6D6D70']}
              outerColor={usingAdvancedFilter ? "#A3F3BE" : "#D1D1D6"}
              borderColor={usingAdvancedFilter ? "#00C851" : "#8E8E93"}
            />
            <Text style={[styles.toolButtonLabel, usingAdvancedFilter && styles.toolButtonLabelActive]}>🔽 筛选</Text>
          </View>
          
          <View style={styles.decorativeButtonWrapper}>
            <DecorativeButton
              onPress={toggleBatchMode}
              iconName="checkmark-circle"
              size="sm"
              gradientColors={['#FF9500', '#FF6B35']}
              outerColor="#FFD60A"
              borderColor="#FF8C00"
            />
            <Text style={styles.toolButtonLabel}>☑️ 选择</Text>
          </View>
          
          <View style={styles.decorativeButtonWrapper}>
            <DecorativeButton
              onPress={() => setShowDataManager(true)}
              iconName="bar-chart"
              size="sm"
              gradientColors={['#5856D6', '#AF52DE']}
              outerColor="#BF5AF2"
              borderColor="#8E44AD"
            />
            <Text style={styles.toolButtonLabel}>📊 管理</Text>
          </View>
          
          <View style={styles.decorativeButtonWrapper}>
            <DecorativeButton
              onPress={fixHistoryData}
              iconName="build"
              size="sm"
              gradientColors={['#FF3B30', '#FF6B35']}
              outerColor="#FF9F0A"
              borderColor="#FF6B00"
            />
            <Text style={styles.toolButtonLabel}>🔧 修复</Text>
          </View>
        </View>
      )}

      {/* 搜索框 */}
      {showSearch && (
        <View style={styles.searchContainer}>
          <TextInput
            style={styles.searchInput}
            placeholder="搜索历史记录..."
            placeholderTextColor={textSecondary}
            value={searchText}
            onChangeText={handleSearchChange}
            autoFocus={true}
            returnKeyType="search"
            clearButtonMode="while-editing"
          />
          {searchText.length > 0 && (
            <Text style={styles.searchResultText}>
              找到 {filteredRecords.length} 条记录
            </Text>
          )}
        </View>
      )}

      {/* 批量操作工具栏 */}
      {batchMode && (
        <View style={styles.batchToolbar}>
          <TouchableOpacity 
            style={styles.selectAllButton}
            onPress={toggleSelectAll}
          >
            <Text style={styles.selectAllText}>
              {selectedRecords.size === filteredRecords.length ? '取消全选' : '全选'}
            </Text>
          </TouchableOpacity>
          
          <Text style={styles.selectedCountText}>
            已选择 {selectedRecords.size} 项
          </Text>
          
          <TouchableOpacity 
            style={styles.dataManagerButton}
            onPress={() => setShowDataManager(true)}
          >
            <Text style={styles.dataManagerText}>
              导出
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.batchDeleteButton, selectedRecords.size === 0 && styles.batchDeleteButtonDisabled]}
            onPress={batchDeleteRecords}
            disabled={selectedRecords.size === 0}
          >
            <Text style={[styles.batchDeleteText, selectedRecords.size === 0 && styles.batchDeleteTextDisabled]}>
              删除
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {/* 统计信息卡片 */}
      {historyRecords.length > 0 && statistics && !showSearch && (
        <View style={styles.statisticsCard}>
          <Text style={styles.statisticsTitle}>📊 批改统计</Text>
          <View style={styles.statisticsGrid}>
            <View style={styles.statisticsItem}>
              <Text style={styles.statisticsValue}>{statistics.totalRecords}</Text>
              <Text style={styles.statisticsLabel}>总记录</Text>
            </View>
            <View style={styles.statisticsItem}>
              <Text style={styles.statisticsValue}>{statistics.totalQuestions}</Text>
              <Text style={styles.statisticsLabel}>总题数</Text>
            </View>
            <View style={styles.statisticsItem}>
              <Text style={[styles.statisticsValue, { color: successColor }]}>
                {statistics.recentActivity ? '今日' : '无'}
              </Text>
              <Text style={styles.statisticsLabel}>最近活动</Text>
            </View>
          </View>
        </View>
      )}

      {/* 学习分析 */}
      {historyRecords.length > 0 && !showSearch && !batchMode && (
        <LearningAnalytics records={filteredRecords} />
      )}

      {/* 学习洞察 */}
      {historyRecords.length >= 3 && !showSearch && !batchMode && (
        <LearningInsights 
          records={filteredRecords}
          onRecommendationPress={(recommendation) => {
            console.log('用户点击建议:', recommendation);
            // 这里可以实现具体的建议处理逻辑
          }}
        />
      )}

      {/* 高级筛选状态 */}
      {usingAdvancedFilter && (
        <View style={styles.filterStatusBar}>
          <Text style={styles.filterStatusText}>
            🔍 筛选已激活 ({filteredRecords.length} 条记录)
          </Text>
          <TouchableOpacity onPress={clearAdvancedFilters} style={styles.clearFilterButton}>
            <Text style={styles.clearFilterText}>清除筛选</Text>
        </TouchableOpacity>
        </View>
      )}

      {/* 历史记录列表 */}
      <View style={styles.container}>
        <FlatList
          data={filteredRecords}
          keyExtractor={(item) => item.id}
          renderItem={renderHistoryItem}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              colors={[primaryColor]}
              tintColor={primaryColor}
            />
          }
          ListEmptyComponent={renderEmptyState}
          contentContainerStyle={filteredRecords.length === 0 ? styles.emptyList : styles.list}
          showsVerticalScrollIndicator={true}
        />
      </View>

      {/* 高级筛选模态框 */}
      <AdvancedFilter
        visible={showAdvancedFilter}
        currentFilters={activeFilters}
        onApplyFilters={applyAdvancedFilters}
        onClose={() => setShowAdvancedFilter(false)}
      />

      {/* 数据管理模态框 */}
      <DataManager
        visible={showDataManager}
        onClose={() => setShowDataManager(false)}
        records={filteredRecords}
        selectedRecords={Array.from(selectedRecords)}
        onDataImported={() => {
          loadHistory();
          setBatchMode(false);
          setSelectedRecords(new Set());
        }}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: backgroundPrimary,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.screenHorizontal,
    paddingVertical: spacing.md,
    backgroundColor: cardBackground,
    borderBottomWidth: 0.5,  // Apple 更轻的分割线
    borderBottomColor: borderColor,
  },
  headerLeft: {
    flex: 1,
  },
  backButton: {
    alignSelf: 'flex-start',
  },
  backButtonText: {
    ...typography.bodyMedium,
    color: primaryColor,
    fontWeight: '400',  // Apple 轻量字体
  },
  headerTitle: {
    ...typography.heading3,
    fontWeight: '500',  // Apple 中等字重
    color: textPrimary,
    textAlign: 'center',
  },
  headerRight: {
    flex: 1,
    alignItems: 'flex-end',
  },
  toolBar: {
    backgroundColor: cardBackground,
    flexDirection: 'row',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    borderBottomWidth: 0.5,
    borderBottomColor: borderColor,
    justifyContent: 'space-around',
    gap: spacing.sm,
  },
  decorativeButtonWrapper: {
    alignItems: 'center',
    gap: spacing.xs,
    flex: 1,
  },
  toolButtonLabel: {
    ...typography.caption,
    color: textPrimary,
    fontWeight: '500',
    textAlign: 'center',
  },
  toolButtonLabelActive: {
    color: successColor,
  },
  toolButton: {
    alignItems: 'center',
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.sm,
    minWidth: 60,
  },
  toolButtonActive: {
    backgroundColor: primaryAlpha10,
  },
  toolButtonIcon: {
    fontSize: 16,
    marginBottom: spacing.xs / 2,
  },
  toolButtonText: {
    ...typography.caption,
    color: textPrimary,
    fontWeight: '400',
  },
  toolButtonTextActive: {
    color: primaryColor,
  },
  fixButton: {
    backgroundColor: errorAlpha10,
  },
  clearButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.md,
    backgroundColor: errorAlpha10,
  },
  clearButtonText: {
    ...typography.bodySmall,
    color: errorColor,
    fontWeight: '400',
  },
  cancelSearchButton: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.sm,
  },
  cancelSearchText: {
    ...typography.bodySmall,
    color: primaryColor,
    fontWeight: '400',
  },
  searchContainer: {
    backgroundColor: cardBackground,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    borderBottomWidth: 0.5,
    borderBottomColor: borderColor,
  },
  searchInput: {
    backgroundColor: backgroundPrimary,
    borderRadius: borderRadius.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    ...typography.bodyMedium,
    color: textPrimary,
    borderWidth: 0.5,
    borderColor: borderColor,
  },
  searchResultText: {
    ...typography.caption,
    color: textSecondary,
    marginTop: spacing.sm,
    textAlign: 'center',
  },
  statisticsCard: {
    backgroundColor: cardBackground,
    marginHorizontal: spacing.md,
    marginVertical: spacing.sm,
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding,
    ...shadows.level1,  // 轻柔阴影
  },
  statisticsTitle: {
    ...typography.heading4,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.md,
    textAlign: 'center',
  },
  statisticsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statisticsItem: {
    alignItems: 'center',
    flex: 1,
  },
  statisticsValue: {
    ...typography.heading3,
    fontWeight: '300',  // Apple 轻量字体
    color: textPrimary,
    marginBottom: spacing.xs,
  },
  statisticsLabel: {
    ...typography.caption,
    color: textSecondary,
    textAlign: 'center',
  },
  filterStatusBar: {
    backgroundColor: primaryAlpha10,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    marginHorizontal: spacing.md,
    marginBottom: spacing.sm,
    borderRadius: borderRadius.sm,
  },
  filterStatusText: {
    ...typography.bodySmall,
    color: primaryColor,
    fontWeight: '400',
  },
  clearFilterButton: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.xs,
    backgroundColor: cardBackground,
  },
  clearFilterText: {
    ...typography.caption,
    color: primaryColor,
    fontWeight: '500',
  },
  batchToolbar: {
    backgroundColor: cardBackground,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    borderBottomWidth: 0.5,
    borderBottomColor: borderColor,
  },
  selectAllButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.sm,
    backgroundColor: primaryAlpha10,
  },
  selectAllText: {
    ...typography.bodySmall,
    color: primaryColor,
    fontWeight: '400',
  },
  selectedCountText: {
    ...typography.bodySmall,
    color: textPrimary,
    flex: 1,
    textAlign: 'center',
  },
  batchDeleteButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.sm,
    backgroundColor: errorAlpha10,
  },
  batchDeleteButtonDisabled: {
    backgroundColor: 'rgba(128, 128, 128, 0.05)',
  },
  batchDeleteText: {
    ...typography.bodySmall,
    color: errorColor,
    fontWeight: '400',
  },
  batchDeleteTextDisabled: {
    color: textSecondary,
  },
  dataManagerButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.sm,
    backgroundColor: successAlpha10,
  },
  dataManagerText: {
    ...typography.bodySmall,
    color: successColor,
    fontWeight: '400',
  },
  container: {
    flex: 1,
  },
  list: {
    padding: spacing.md,
  },
  emptyList: {
    flex: 1,
    justifyContent: 'center',
  },
  historyItem: {
    backgroundColor: cardBackground,
    borderRadius: borderRadius.card,
    padding: spacing.cardPadding,
    marginBottom: spacing.md,
    ...shadows.level1,  // 轻柔阴影
  },
  historyItemBatch: {
    borderWidth: 1.5,  // Apple 精细边框
    borderColor: borderColor,
  },
  historyItemSelected: {
    borderColor: primaryColor,
    backgroundColor: primaryAlpha10,
  },
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  checkboxContainer: {
    marginRight: spacing.md,
  },
  checkbox: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 1.5,
    borderColor: borderColor,
    backgroundColor: backgroundPrimary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkboxSelected: {
    borderColor: primaryColor,
    backgroundColor: primaryColor,
  },
  checkmark: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  timeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  timeIcon: {
    fontSize: 16,
    marginRight: spacing.sm,
  },
  timeText: {
    ...typography.heading4,
    fontWeight: '500',
    color: textPrimary,
  },
  deleteButton: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.sm,
    backgroundColor: errorAlpha10,
  },
  deleteButtonText: {
    ...typography.caption,
    color: errorColor,
    fontWeight: '400',
  },
  itemContent: {
    flexDirection: 'row',
    marginBottom: spacing.md,
  },
  imagePreview: {
    marginRight: spacing.md,
  },
  thumbnailImage: {
    width: 60,
    height: 60,
    borderRadius: borderRadius.sm,
    backgroundColor: backgroundPrimary,
  },
  summaryContainer: {
    flex: 1,
  },
  summaryTitle: {
    ...typography.bodySmall,
    fontWeight: '400',
    color: textPrimary,
    marginBottom: spacing.sm,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    ...typography.heading4,
    fontWeight: '500',
    color: textPrimary,
  },
  statLabel: {
    ...typography.caption,
    color: textSecondary,
    marginTop: spacing.xs / 2,
  },
  itemFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: spacing.md,
    borderTopWidth: 0.5,  // Apple 精细分割线
    borderTopColor: borderColor,
  },
  taskId: {
    ...typography.caption,
    color: textSecondary,
  },
  viewDetail: {
    ...typography.caption,
    color: primaryColor,
    fontWeight: '400',
  },
  emptyContainer: {
    alignItems: 'center',
    paddingHorizontal: spacing.xxxl,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: spacing.md,
  },
  emptyTitle: {
    ...typography.heading3,
    fontWeight: '500',
    color: textPrimary,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  emptyDescription: {
    ...typography.bodySmall,
    color: textSecondary,
    textAlign: 'center',
  },
});

export default HistoryScreen;