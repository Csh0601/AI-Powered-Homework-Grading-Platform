import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  ScrollView,
  TextInput,
  Switch,
  Alert,
} from 'react-native';
import { HistoryFilters, FilterPreset, DateRangePreset } from '../types/HistoryTypes';
import historyService from '../services/historyService';
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

interface AdvancedFilterProps {
  visible: boolean;
  currentFilters: HistoryFilters;
  onApplyFilters: (filters: HistoryFilters) => void;
  onClose: () => void;
}

const AdvancedFilter: React.FC<AdvancedFilterProps> = ({
  visible,
  currentFilters,
  onApplyFilters,
  onClose,
}) => {
  const [filters, setFilters] = useState<HistoryFilters>(currentFilters);
  const [activeTab, setActiveTab] = useState<'presets' | 'custom'>('presets');

  // 应用筛选
  const handleApplyFilters = useCallback(() => {
    onApplyFilters(filters);
    onClose();
  }, [filters, onApplyFilters, onClose]);

  // 重置筛选
  const handleResetFilters = useCallback(() => {
    const emptyFilters: HistoryFilters = {};
    setFilters(emptyFilters);
    onApplyFilters(emptyFilters);
    onClose();
  }, [onApplyFilters, onClose]);

  // 应用预设筛选
  const applyPreset = useCallback((preset: FilterPreset) => {
    setFilters(preset.filters);
    onApplyFilters(preset.filters);
    onClose();
  }, [onApplyFilters, onClose]);

  // 应用日期范围预设
  const applyDateRange = useCallback((preset: DateRangePreset) => {
    const { startDate, endDate } = preset.getDateRange();
    const newFilters = { ...filters, startDate, endDate };
    setFilters(newFilters);
  }, [filters]);

  // 更新筛选条件
  const updateFilter = useCallback((key: keyof HistoryFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  }, []);

  // 检查是否有活动的筛选
  const hasActiveFilters = useCallback(() => {
    return Object.keys(filters).length > 0;
  }, [filters]);

  const filterPresets = historyService.getFilterPresets();
  const dateRangePresets = historyService.getDateRangePresets();

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
            <Text style={styles.closeButtonText}>取消</Text>
          </TouchableOpacity>
          
          <Text style={styles.title}>高级筛选</Text>
          
          <TouchableOpacity onPress={handleApplyFilters} style={styles.applyButton}>
            <Text style={styles.applyButtonText}>应用</Text>
          </TouchableOpacity>
        </View>

        {/* 标签页 */}
        <View style={styles.tabContainer}>
          <TouchableOpacity
            style={[styles.tab, activeTab === 'presets' && styles.activeTab]}
            onPress={() => setActiveTab('presets')}
          >
            <Text style={[styles.tabText, activeTab === 'presets' && styles.activeTabText]}>
              快速筛选
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.tab, activeTab === 'custom' && styles.activeTab]}
            onPress={() => setActiveTab('custom')}
          >
            <Text style={[styles.tabText, activeTab === 'custom' && styles.activeTabText]}>
              自定义筛选
            </Text>
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {activeTab === 'presets' ? (
            // 预设筛选
            <View style={styles.presetsContainer}>
              <Text style={styles.sectionTitle}>筛选预设</Text>
              <View style={styles.presetGrid}>
                {filterPresets.map((preset) => (
                  <TouchableOpacity
                    key={preset.id}
                    style={styles.presetItem}
                    onPress={() => applyPreset(preset)}
                  >
                    <Text style={styles.presetIcon}>{preset.icon}</Text>
                    <Text style={styles.presetName}>{preset.name}</Text>
                  </TouchableOpacity>
                ))}
              </View>

              <Text style={styles.sectionTitle}>日期范围</Text>
              <View style={styles.dateRangeGrid}>
                {dateRangePresets.map((preset) => (
                  <TouchableOpacity
                    key={preset.id}
                    style={styles.dateRangeItem}
                    onPress={() => applyDateRange(preset)}
                  >
                    <Text style={styles.dateRangeText}>{preset.name}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          ) : (
            // 自定义筛选
            <View style={styles.customContainer}>
              {/* 分数范围 */}
              <View style={styles.filterSection}>
                <Text style={styles.sectionTitle}>分数范围</Text>
                <View style={styles.rangeInputContainer}>
                  <TextInput
                    style={styles.rangeInput}
                    placeholder="最低分"
                    placeholderTextColor={secondaryTextColor}
                    value={filters.minScore?.toString() || ''}
                    onChangeText={(text) => updateFilter('minScore', text ? parseFloat(text) : undefined)}
                    keyboardType="numeric"
                  />
                  <Text style={styles.rangeSeparator}>-</Text>
                  <TextInput
                    style={styles.rangeInput}
                    placeholder="最高分"
                    placeholderTextColor={secondaryTextColor}
                    value={filters.maxScore?.toString() || ''}
                    onChangeText={(text) => updateFilter('maxScore', text ? parseFloat(text) : undefined)}
                    keyboardType="numeric"
                  />
                </View>
              </View>

              {/* 正确率范围 */}
              <View style={styles.filterSection}>
                <Text style={styles.sectionTitle}>正确率范围 (%)</Text>
                <View style={styles.rangeInputContainer}>
                  <TextInput
                    style={styles.rangeInput}
                    placeholder="最低正确率"
                    placeholderTextColor={secondaryTextColor}
                    value={filters.minCorrectRate?.toString() || ''}
                    onChangeText={(text) => updateFilter('minCorrectRate', text ? parseFloat(text) : undefined)}
                    keyboardType="numeric"
                  />
                  <Text style={styles.rangeSeparator}>-</Text>
                  <TextInput
                    style={styles.rangeInput}
                    placeholder="最高正确率"
                    placeholderTextColor={secondaryTextColor}
                    value={filters.maxCorrectRate?.toString() || ''}
                    onChangeText={(text) => updateFilter('maxCorrectRate', text ? parseFloat(text) : undefined)}
                    keyboardType="numeric"
                  />
                </View>
              </View>

              {/* 题目数量范围 */}
              <View style={styles.filterSection}>
                <Text style={styles.sectionTitle}>题目数量范围</Text>
                <View style={styles.rangeInputContainer}>
                  <TextInput
                    style={styles.rangeInput}
                    placeholder="最少题数"
                    placeholderTextColor={secondaryTextColor}
                    value={filters.questionCountRange?.min?.toString() || ''}
                    onChangeText={(text) => updateFilter('questionCountRange', {
                      ...filters.questionCountRange,
                      min: text ? parseInt(text) : undefined
                    })}
                    keyboardType="numeric"
                  />
                  <Text style={styles.rangeSeparator}>-</Text>
                  <TextInput
                    style={styles.rangeInput}
                    placeholder="最多题数"
                    placeholderTextColor={secondaryTextColor}
                    value={filters.questionCountRange?.max?.toString() || ''}
                    onChangeText={(text) => updateFilter('questionCountRange', {
                      ...filters.questionCountRange,
                      max: text ? parseInt(text) : undefined
                    })}
                    keyboardType="numeric"
                  />
                </View>
              </View>

              {/* 错题筛选 */}
              <View style={styles.filterSection}>
                <View style={styles.switchContainer}>
                  <Text style={styles.sectionTitle}>只显示有错题的记录</Text>
                  <Switch
                    value={filters.hasErrors === true}
                    onValueChange={(value) => updateFilter('hasErrors', value ? true : undefined)}
                    trackColor={{ false: borderColor, true: primaryColor }}
                    thumbColor={filters.hasErrors === true ? '#fff' : '#f4f3f4'}
                  />
                </View>
              </View>
            </View>
          )}
        </ScrollView>

        {/* 底部操作栏 */}
        <View style={styles.bottomBar}>
          {hasActiveFilters() && (
            <TouchableOpacity onPress={handleResetFilters} style={styles.resetButton}>
              <Text style={styles.resetButtonText}>重置筛选</Text>
            </TouchableOpacity>
          )}
          
          <Text style={styles.filterStatus}>
            {hasActiveFilters() ? '筛选已激活' : '无筛选条件'}
          </Text>
        </View>
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
    color: secondaryTextColor,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: textColor,
  },
  applyButton: {
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  applyButtonText: {
    fontSize: 16,
    color: primaryColor,
    fontWeight: '600',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: cardBackgroundColor,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: borderColor,
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  activeTab: {
    borderBottomColor: primaryColor,
  },
  tabText: {
    fontSize: 16,
    color: secondaryTextColor,
  },
  activeTabText: {
    color: primaryColor,
    fontWeight: '600',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  presetsContainer: {
    gap: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: textColor,
    marginBottom: 12,
  },
  presetGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  presetItem: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    minWidth: 80,
    borderWidth: 1,
    borderColor: borderColor,
  },
  presetIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  presetName: {
    fontSize: 12,
    color: textColor,
    textAlign: 'center',
  },
  dateRangeGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  dateRangeItem: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: borderColor,
  },
  dateRangeText: {
    fontSize: 14,
    color: textColor,
  },
  customContainer: {
    gap: 20,
  },
  filterSection: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: borderColor,
  },
  rangeInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  rangeInput: {
    flex: 1,
    backgroundColor: backgroundColor,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 16,
    color: textColor,
    borderWidth: 1,
    borderColor: borderColor,
  },
  rangeSeparator: {
    fontSize: 16,
    color: secondaryTextColor,
  },
  switchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  bottomBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: cardBackgroundColor,
    borderTopWidth: 1,
    borderTopColor: borderColor,
  },
  resetButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: 'rgba(255, 59, 48, 0.1)',
  },
  resetButtonText: {
    fontSize: 14,
    color: errorColor,
    fontWeight: '500',
  },
  filterStatus: {
    fontSize: 12,
    color: secondaryTextColor,
  },
});

export default AdvancedFilter;
