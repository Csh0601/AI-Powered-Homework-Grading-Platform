import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  ScrollView,
  Alert,
  Switch,
  TextInput,
  ActivityIndicator,
} from 'react-native';
import { HistoryRecord } from '../types/HistoryTypes';
import dataExportService, { ExportOptions } from '../services/dataExportService';
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

interface DataManagerProps {
  visible: boolean;
  onClose: () => void;
  records: HistoryRecord[];
  selectedRecords?: string[];
  onDataImported?: () => void;
}

const DataManager: React.FC<DataManagerProps> = ({
  visible,
  onClose,
  records,
  selectedRecords = [],
  onDataImported,
}) => {
  const [activeTab, setActiveTab] = useState<'export' | 'import'>('export');
  const [loading, setLoading] = useState(false);
  
  // 导出选项
  const [exportFormat, setExportFormat] = useState<'json' | 'csv'>('json');
  const [includeImages, setIncludeImages] = useState(true);
  const [exportSelected, setExportSelected] = useState(false);
  const [dateRangeExport, setDateRangeExport] = useState(false);
  
  // 导入选项
  const [importData, setImportData] = useState('');
  const [mergeMode, setMergeMode] = useState<'replace' | 'merge' | 'append'>('merge');
  const [skipDuplicates, setSkipDuplicates] = useState(true);

  // 导出数据
  const handleExport = useCallback(async () => {
    try {
      setLoading(true);
      
      const options: ExportOptions = {
        format: exportFormat,
        includeImages,
      };

      // 如果选择导出已选中的记录
      if (exportSelected && selectedRecords.length > 0) {
        options.selectedRecords = selectedRecords;
      }

      // 如果需要日期范围（这里简化为最近30天）
      if (dateRangeExport) {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - 30);
        options.dateRange = { startDate, endDate };
      }

      const exportedData = await dataExportService.exportData(options);
      const fileName = dataExportService.generateFileName(exportFormat);
      
      // 这里在实际应用中应该使用文件系统API保存文件
      // 目前只是显示数据预览
      Alert.alert(
        '导出成功',
        `数据已准备就绪\n文件名: ${fileName}\n大小: ${Math.round(exportedData.length / 1024)} KB`,
        [
          { text: '确定' },
          {
            text: '预览数据',
            onPress: () => {
              Alert.alert(
                '数据预览',
                exportedData.length > 500 
                  ? exportedData.substring(0, 500) + '...'
                  : exportedData
              );
            }
          }
        ]
      );

      console.log('📤 导出完成:', { fileName, size: exportedData.length });
    } catch (error) {
      console.error('导出失败:', error);
      Alert.alert('导出失败', `导出过程中出现错误: ${error}`);
    } finally {
      setLoading(false);
    }
  }, [exportFormat, includeImages, exportSelected, selectedRecords, dateRangeExport]);

  // 导入数据
  const handleImport = useCallback(async () => {
    if (!importData.trim()) {
      Alert.alert('提示', '请输入要导入的数据');
      return;
    }

    try {
      setLoading(true);

      // 验证数据格式
      const validation = dataExportService.validateImportData(importData);
      if (!validation.isValid) {
        Alert.alert('数据格式错误', validation.error || '数据格式不正确');
        return;
      }

      if (!validation.data) {
        Alert.alert('错误', '无法解析导入数据');
        return;
      }

      // 确认导入
      Alert.alert(
        '确认导入',
        `即将导入 ${validation.data.totalRecords} 条记录\n导出时间: ${new Date(validation.data.exportDate).toLocaleString()}\n合并模式: ${
          mergeMode === 'replace' ? '替换所有' :
          mergeMode === 'merge' ? '合并数据' : '追加数据'
        }`,
        [
          { text: '取消', style: 'cancel' },
          {
            text: '确认导入',
            style: 'destructive',
            onPress: async () => {
              try {
                const result = await dataExportService.importData(validation.data!, {
                  mergeMode,
                  skipDuplicates,
                });

                const message = `导入完成\n成功: ${result.imported} 条\n跳过: ${result.skipped} 条${
                  result.errors.length > 0 ? `\n错误: ${result.errors.length} 条` : ''
                }`;

                Alert.alert(
                  result.success ? '导入成功' : '导入完成(有错误)',
                  message,
                  [
                    { text: '确定' },
                    result.errors.length > 0 ? {
                      text: '查看错误',
                      onPress: () => Alert.alert('导入错误', result.errors.join('\n'))
                    } : undefined
                  ].filter(Boolean) as any
                );

                if (result.imported > 0 && onDataImported) {
                  onDataImported();
                }

                // 清空输入
                setImportData('');
              } catch (error) {
                Alert.alert('导入失败', `导入过程中出现错误: ${error}`);
              }
            }
          }
        ]
      );
    } catch (error) {
      console.error('导入失败:', error);
      Alert.alert('导入失败', `导入过程中出现错误: ${error}`);
    } finally {
      setLoading(false);
    }
  }, [importData, mergeMode, skipDuplicates, onDataImported]);

  // 生成示例数据
  const generateSampleData = useCallback(async () => {
    try {
      const sampleRecords = records.slice(0, 2); // 取前两条作为示例
      if (sampleRecords.length === 0) {
        Alert.alert('提示', '暂无数据可生成示例');
        return;
      }

      const options: ExportOptions = {
        format: 'json',
        includeImages: false,
        selectedRecords: sampleRecords.map(r => r.id),
      };

      const sampleData = await dataExportService.exportData(options);
      setImportData(sampleData);
      Alert.alert('示例生成', '已生成示例数据，您可以修改后导入');
    } catch (error) {
      Alert.alert('生成失败', `生成示例数据失败: ${error}`);
    }
  }, [records]);

  const renderExportTab = () => (
    <View style={styles.tabContent}>
      <Text style={styles.sectionTitle}>导出选项</Text>
      
      {/* 导出格式 */}
      <View style={styles.optionGroup}>
        <Text style={styles.optionLabel}>导出格式</Text>
        <View style={styles.formatButtons}>
          <TouchableOpacity
            style={[styles.formatButton, exportFormat === 'json' && styles.formatButtonActive]}
            onPress={() => setExportFormat('json')}
          >
            <Text style={[styles.formatButtonText, exportFormat === 'json' && styles.formatButtonTextActive]}>
              JSON
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.formatButton, exportFormat === 'csv' && styles.formatButtonActive]}
            onPress={() => setExportFormat('csv')}
          >
            <Text style={[styles.formatButtonText, exportFormat === 'csv' && styles.formatButtonTextActive]}>
              CSV
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* 导出选项 */}
      <View style={styles.optionGroup}>
        <View style={styles.switchOption}>
          <Text style={styles.optionLabel}>包含图片数据</Text>
          <Switch
            value={includeImages}
            onValueChange={setIncludeImages}
            trackColor={{ false: borderColor, true: primaryColor }}
            thumbColor={includeImages ? '#fff' : '#f4f3f4'}
          />
        </View>
        
        {selectedRecords.length > 0 && (
          <View style={styles.switchOption}>
            <Text style={styles.optionLabel}>只导出选中记录 ({selectedRecords.length} 条)</Text>
            <Switch
              value={exportSelected}
              onValueChange={setExportSelected}
              trackColor={{ false: borderColor, true: primaryColor }}
              thumbColor={exportSelected ? '#fff' : '#f4f3f4'}
            />
          </View>
        )}

        <View style={styles.switchOption}>
          <Text style={styles.optionLabel}>限制日期范围 (最近30天)</Text>
          <Switch
            value={dateRangeExport}
            onValueChange={setDateRangeExport}
            trackColor={{ false: borderColor, true: primaryColor }}
            thumbColor={dateRangeExport ? '#fff' : '#f4f3f4'}
          />
        </View>
      </View>

      {/* 导出按钮 */}
      <TouchableOpacity
        style={[styles.actionButton, styles.exportButton]}
        onPress={handleExport}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.actionButtonText}>
            📤 导出数据 ({exportSelected && selectedRecords.length > 0 
              ? selectedRecords.length 
              : records.length} 条)
          </Text>
        )}
      </TouchableOpacity>
    </View>
  );

  const renderImportTab = () => (
    <View style={styles.tabContent}>
      <Text style={styles.sectionTitle}>导入选项</Text>

      {/* 合并模式 */}
      <View style={styles.optionGroup}>
        <Text style={styles.optionLabel}>合并模式</Text>
        <View style={styles.mergeModeButtons}>
          {[
            { key: 'merge' as const, label: '合并', desc: '保留现有数据，合并新数据' },
            { key: 'append' as const, label: '追加', desc: '在现有数据后添加' },
            { key: 'replace' as const, label: '替换', desc: '删除所有现有数据' },
          ].map(mode => (
            <TouchableOpacity
              key={mode.key}
              style={[styles.mergeModeButton, mergeMode === mode.key && styles.mergeModeButtonActive]}
              onPress={() => setMergeMode(mode.key)}
            >
              <Text style={[styles.mergeModeButtonText, mergeMode === mode.key && styles.mergeModeButtonTextActive]}>
                {mode.label}
              </Text>
              <Text style={styles.mergeModeDesc}>{mode.desc}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* 重复处理 */}
      <View style={styles.optionGroup}>
        <View style={styles.switchOption}>
          <Text style={styles.optionLabel}>跳过重复记录</Text>
          <Switch
            value={skipDuplicates}
            onValueChange={setSkipDuplicates}
            trackColor={{ false: borderColor, true: primaryColor }}
            thumbColor={skipDuplicates ? '#fff' : '#f4f3f4'}
          />
        </View>
      </View>

      {/* 数据输入 */}
      <View style={styles.optionGroup}>
        <Text style={styles.optionLabel}>导入数据 (JSON格式)</Text>
        <TextInput
          style={styles.dataInput}
          multiline
          placeholder="粘贴导出的JSON数据..."
          placeholderTextColor={secondaryTextColor}
          value={importData}
          onChangeText={setImportData}
          textAlignVertical="top"
        />
        
        <TouchableOpacity
          style={styles.sampleButton}
          onPress={generateSampleData}
        >
          <Text style={styles.sampleButtonText}>生成示例数据</Text>
        </TouchableOpacity>
      </View>

      {/* 导入按钮 */}
      <TouchableOpacity
        style={[styles.actionButton, styles.importButton]}
        onPress={handleImport}
        disabled={loading || !importData.trim()}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.actionButtonText}>📥 导入数据</Text>
        )}
      </TouchableOpacity>
    </View>
  );

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
          
          <Text style={styles.title}>数据管理</Text>
          
          <View style={styles.headerSpacer} />
        </View>

        {/* 标签页 */}
        <View style={styles.tabContainer}>
          <TouchableOpacity
            style={[styles.tab, activeTab === 'export' && styles.activeTab]}
            onPress={() => setActiveTab('export')}
          >
            <Text style={[styles.tabText, activeTab === 'export' && styles.activeTabText]}>
              导出数据
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.tab, activeTab === 'import' && styles.activeTab]}
            onPress={() => setActiveTab('import')}
          >
            <Text style={[styles.tabText, activeTab === 'import' && styles.activeTabText]}>
              导入数据
            </Text>
          </TouchableOpacity>
        </View>

        {/* 内容区域 */}
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {activeTab === 'export' ? renderExportTab() : renderImportTab()}
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
    width: 60, // 平衡右侧空间
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
  },
  tabContent: {
    padding: 20,
    gap: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: textColor,
    marginBottom: 8,
  },
  optionGroup: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: borderColor,
    gap: 12,
  },
  optionLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: textColor,
  },
  formatButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  formatButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    backgroundColor: backgroundColor,
    borderWidth: 1,
    borderColor: borderColor,
    alignItems: 'center',
  },
  formatButtonActive: {
    backgroundColor: primaryColor,
    borderColor: primaryColor,
  },
  formatButtonText: {
    fontSize: 14,
    color: textColor,
    fontWeight: '500',
  },
  formatButtonTextActive: {
    color: '#fff',
  },
  switchOption: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  mergeModeButtons: {
    gap: 8,
  },
  mergeModeButton: {
    padding: 12,
    borderRadius: 8,
    backgroundColor: backgroundColor,
    borderWidth: 1,
    borderColor: borderColor,
  },
  mergeModeButtonActive: {
    backgroundColor: 'rgba(0, 122, 255, 0.1)',
    borderColor: primaryColor,
  },
  mergeModeButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: textColor,
    marginBottom: 4,
  },
  mergeModeButtonTextActive: {
    color: primaryColor,
  },
  mergeModeDesc: {
    fontSize: 12,
    color: secondaryTextColor,
  },
  dataInput: {
    backgroundColor: backgroundColor,
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    color: textColor,
    borderWidth: 1,
    borderColor: borderColor,
    height: 120,
    fontFamily: 'monospace',
  },
  sampleButton: {
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    backgroundColor: 'rgba(0, 122, 255, 0.1)',
  },
  sampleButtonText: {
    fontSize: 12,
    color: primaryColor,
    fontWeight: '500',
  },
  actionButton: {
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 10,
  },
  exportButton: {
    backgroundColor: successColor,
  },
  importButton: {
    backgroundColor: primaryColor,
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default DataManager;
