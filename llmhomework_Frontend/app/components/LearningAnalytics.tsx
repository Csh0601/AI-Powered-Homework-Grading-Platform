import React, { useState, useEffect, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
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
} from '../styles/colors';

interface LearningAnalyticsProps {
  records: HistoryRecord[];
}

interface ChartData {
  label: string;
  value: number;
  color: string;
  date?: string;
}

interface TrendData {
  date: string;
  correctRate: number;
  totalQuestions: number;
  score?: number;
}

const LearningAnalytics: React.FC<LearningAnalyticsProps> = ({ records }) => {
  const [activeChart, setActiveChart] = useState<'trend' | 'distribution' | 'performance'>('trend');
  const windowWidth = Dimensions.get('window').width;
  const chartWidth = windowWidth - 40;
  const chartHeight = 220;

  // 计算扩展的趋势数据（包含未来日期）
  const trendData = useMemo(() => {
    if (!records || records.length === 0) return { dataPoints: [], allDates: [] };

    // 按日期分组
    const groupedByDate: { [key: string]: HistoryRecord[] } = {};
    records.forEach(record => {
      const date = new Date(record.timestamp);
      const dateKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
      
      if (!groupedByDate[dateKey]) {
        groupedByDate[dateKey] = [];
      }
      groupedByDate[dateKey].push(record);
    });

    // 计算每日统计
    const dataPoints: TrendData[] = Object.entries(groupedByDate)
      .map(([date, dayRecords]) => {
        let totalQuestions = 0;
        let totalCorrect = 0;
        let totalScore = 0;
        let scoreCount = 0;

        dayRecords.forEach(record => {
          if (record.summary) {
            totalQuestions += record.summary.totalQuestions;
            totalCorrect += record.summary.correctCount;
            if (record.summary.score !== undefined) {
              totalScore += record.summary.score;
              scoreCount++;
            }
          }
        });

        const correctRate = totalQuestions > 0 ? (totalCorrect / totalQuestions) * 100 : 0;
        const avgScore = scoreCount > 0 ? totalScore / scoreCount : undefined;

        return {
          date,
          correctRate: Math.round(correctRate * 10) / 10,
          totalQuestions,
          score: avgScore,
        };
      })
      .sort((a, b) => a.date.localeCompare(b.date));

    // 生成完整的日期范围（包含未来2天）
    const today = new Date();
    const allDates: string[] = [];
    
    // 如果有数据，从最早的数据开始，否则从今天开始
    const startDate = dataPoints.length > 0 ? new Date(dataPoints[0].date) : today;
    
    // 生成从开始日期到未来2天的所有日期
    const endDate = new Date(today);
    endDate.setDate(today.getDate() + 2); // 未来2天
    
    const currentDate = new Date(startDate);
    while (currentDate <= endDate) {
      const dateKey = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(currentDate.getDate()).padStart(2, '0')}`;
      allDates.push(dateKey);
      currentDate.setDate(currentDate.getDate() + 1);
    }

    return { dataPoints, allDates };
  }, [records]);

  // 计算正确率分布数据
  const distributionData = useMemo((): ChartData[] => {
    if (!records || records.length === 0) return [];

    const ranges = [
      { label: '0-20%', min: 0, max: 20, color: '#FF3B30' },
      { label: '21-40%', min: 21, max: 40, color: '#FF9500' },
      { label: '41-60%', min: 41, max: 60, color: '#FFCC00' },
      { label: '61-80%', min: 61, max: 80, color: '#30D158' },
      { label: '81-100%', min: 81, max: 100, color: '#007AFF' },
    ];

    const distribution = ranges.map(range => ({ ...range, value: 0 }));

    records.forEach(record => {
      if (record.summary && record.summary.totalQuestions > 0) {
        const correctRate = (record.summary.correctCount / record.summary.totalQuestions) * 100;
        const rangeIndex = distribution.findIndex(range => 
          correctRate >= range.min && correctRate <= range.max
        );
        if (rangeIndex !== -1) {
          distribution[rangeIndex].value++;
        }
      }
    });

    return distribution;
  }, [records]);

  // 计算性能统计
  const performanceStats = useMemo(() => {
    if (!records || records.length === 0) {
      return {
        totalRecords: 0,
        totalQuestions: 0,
        averageCorrectRate: 0,
        bestPerformance: null,
        worstPerformance: null,
        improvementTrend: 0,
      };
    }

    let totalQuestions = 0;
    let totalCorrect = 0;
    let bestRate = 0;
    let worstRate = 100;
    let bestRecord: HistoryRecord | null = null;
    let worstRecord: HistoryRecord | null = null;

    records.forEach(record => {
      if (record.summary && record.summary.totalQuestions > 0) {
        totalQuestions += record.summary.totalQuestions;
        totalCorrect += record.summary.correctCount;
        
        const correctRate = (record.summary.correctCount / record.summary.totalQuestions) * 100;
        if (correctRate > bestRate) {
          bestRate = correctRate;
          bestRecord = record;
        }
        if (correctRate < worstRate) {
          worstRate = correctRate;
          worstRecord = record;
        }
      }
    });

    const averageCorrectRate = totalQuestions > 0 ? (totalCorrect / totalQuestions) * 100 : 0;

    // 计算改进趋势（比较最近3次和之前3次的平均正确率）
    let improvementTrend = 0;
    if (records.length >= 6) {
      const recent = records.slice(0, 3);
      const previous = records.slice(3, 6);
      
      const recentAvg = recent.reduce((sum, r) => {
        if (!r.summary || r.summary.totalQuestions === 0) return sum;
        return sum + (r.summary.correctCount / r.summary.totalQuestions) * 100;
      }, 0) / recent.length;
      
      const previousAvg = previous.reduce((sum, r) => {
        if (!r.summary || r.summary.totalQuestions === 0) return sum;
        return sum + (r.summary.correctCount / r.summary.totalQuestions) * 100;
      }, 0) / previous.length;
      
      improvementTrend = recentAvg - previousAvg;
    }

    return {
      totalRecords: records.length,
      totalQuestions,
      averageCorrectRate: Math.round(averageCorrectRate * 10) / 10,
      bestPerformance: bestRecord,
      worstPerformance: worstRecord,
      improvementTrend: Math.round(improvementTrend * 10) / 10,
    };
  }, [records]);

  // 渲染趋势图
  const renderTrendChart = () => {
    if (trendData.allDates.length === 0) {
      return (
        <View style={styles.emptyChart}>
          <Text style={styles.emptyChartText}>暂无数据</Text>
        </View>
      );
    }

    const { dataPoints, allDates } = trendData;
    const maxRate = dataPoints.length > 0 ? Math.max(...dataPoints.map(d => d.correctRate), 100) : 100;
    const minRate = dataPoints.length > 0 ? Math.min(...dataPoints.map(d => d.correctRate), 0) : 0;
    const range = maxRate - minRate || 100;

    // 计算滚动区域的宽度：每个日期点占用80px
    const pointWidth = 80;
    const scrollWidth = Math.max(allDates.length * pointWidth, chartWidth);
    const today = new Date().toISOString().split('T')[0];

    return (
      <View style={styles.chartContainer}>
        <View style={[styles.chart, { width: chartWidth, height: chartHeight }]}>
          {/* Y轴标签 */}
          <View style={styles.yAxis}>
            <Text style={styles.axisLabel}>100%</Text>
            <Text style={styles.axisLabel}>75%</Text>
            <Text style={styles.axisLabel}>50%</Text>
            <Text style={styles.axisLabel}>25%</Text>
            <Text style={styles.axisLabel}>0%</Text>
          </View>
          
          {/* 可滚动的图表区域 */}
          <ScrollView 
            horizontal 
            showsHorizontalScrollIndicator={false}
            style={styles.scrollableChart}
            contentContainerStyle={{ width: scrollWidth }}
          >
            <View style={[styles.chartArea, { width: scrollWidth }]}>
              {/* 网格线 */}
              <View style={styles.gridLines}>
                {[0, 25, 50, 75, 100].map(value => (
                  <View key={value} style={[styles.gridLine, { bottom: `${value}%` }]} />
                ))}
              </View>
              
              {/* 数据点和连线 */}
              <View style={styles.dataArea}>
                {allDates.map((date, index) => {
                  // 查找对应日期的数据点
                  const dataPoint = dataPoints.find(dp => dp.date === date);
                  const x = (index * pointWidth) + (pointWidth / 2);
                  
                  // 只渲染有数据的点
                  if (dataPoint) {
                    const y = ((dataPoint.correctRate - minRate) / range) * 100;
                    const adjustedY = Math.max(Math.min(y, 85), 10);
                    
                    return (
                      <View
                        key={date}
                        style={[
                          styles.dataPoint,
                          {
                            left: x - 4, // 减去点的半径
                            bottom: `${adjustedY}%`,
                            backgroundColor: dataPoint.correctRate >= 80 ? successColor : 
                                           dataPoint.correctRate >= 60 ? primaryColor : errorColor,
                          }
                        ]}
                      >
                        <Text style={styles.dataPointText}>{dataPoint.correctRate}%</Text>
                      </View>
                    );
                  }
                  return null;
                })}
              </View>
            </View>
          </ScrollView>
        </View>
        
        {/* 可滚动的X轴标签 */}
        <ScrollView 
          horizontal 
          showsHorizontalScrollIndicator={false}
          style={styles.scrollableXAxis}
          contentContainerStyle={{ width: scrollWidth }}
        >
          <View style={[styles.xAxis, { width: scrollWidth, paddingHorizontal: 0 }]}>
            {allDates.map((date, index) => {
              const isToday = date === today;
              const isFuture = new Date(date) > new Date(today);
              
              return (
                <View 
                  key={date} 
                  style={[
                    styles.xAxisLabelContainer,
                    { width: pointWidth }
                  ]}
                >
                  <Text style={[
                    styles.xAxisLabel,
                    isToday && styles.todayLabel,
                    isFuture && styles.futureLabel
                  ]}>
                    {date.split('-').slice(1).join('/')}
                  </Text>
                  {isToday && <Text style={styles.todayIndicator}>今日</Text>}
                </View>
              );
            })}
          </View>
        </ScrollView>
      </View>
    );
  };

  // 渲染分布图
  const renderDistributionChart = () => {
    const maxValue = Math.max(...distributionData.map(d => d.value), 1);
    
    return (
      <View style={styles.distributionChart}>
        {distributionData.map((item, index) => {
          const height = (item.value / maxValue) * 150;
          return (
            <View key={item.label} style={styles.distributionBar}>
              <View
                style={[
                  styles.bar,
                  {
                    height: height,
                    backgroundColor: item.color,
                  }
                ]}
              >
                {item.value > 0 && (
                  <Text style={styles.barValue}>{item.value}</Text>
                )}
              </View>
              <Text style={styles.barLabel}>{item.label}</Text>
            </View>
          );
        })}
      </View>
    );
  };

  // 渲染性能统计
  const renderPerformanceStats = () => (
    <View style={styles.performanceContainer}>
      <View style={styles.statsGrid}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{performanceStats.totalRecords}</Text>
          <Text style={styles.statLabel}>总记录数</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{performanceStats.totalQuestions}</Text>
          <Text style={styles.statLabel}>总题目数</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={[styles.statValue, { color: primaryColor }]}>
            {performanceStats.averageCorrectRate}%
          </Text>
          <Text style={styles.statLabel}>平均正确率</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={[
            styles.statValue, 
            { color: performanceStats.improvementTrend >= 0 ? successColor : errorColor }
          ]}>
            {performanceStats.improvementTrend >= 0 ? '+' : ''}{performanceStats.improvementTrend}%
          </Text>
          <Text style={styles.statLabel}>进步趋势</Text>
        </View>
      </View>
    </View>
  );

  if (!records || records.length === 0) {
    return (
      <View style={styles.container}>
        <Text style={styles.emptyText}>暂无学习数据</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* 标签页 */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeChart === 'trend' && styles.activeTab]}
          onPress={() => setActiveChart('trend')}
        >
          <Text style={[styles.tabText, activeChart === 'trend' && styles.activeTabText]}>
            趋势图
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, activeChart === 'distribution' && styles.activeTab]}
          onPress={() => setActiveChart('distribution')}
        >
          <Text style={[styles.tabText, activeChart === 'distribution' && styles.activeTabText]}>
            分布图
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, activeChart === 'performance' && styles.activeTab]}
          onPress={() => setActiveChart('performance')}
        >
          <Text style={[styles.tabText, activeChart === 'performance' && styles.activeTabText]}>
            统计
          </Text>
        </TouchableOpacity>
      </View>

      {/* 图表内容 */}
      <ScrollView 
        style={styles.chartContent} 
        contentContainerStyle={styles.chartContentContainer}
        showsVerticalScrollIndicator={false}
        bounces={false}
        decelerationRate="fast"
        scrollEventThrottle={16}
      >
        {activeChart === 'trend' && renderTrendChart()}
        {activeChart === 'distribution' && renderDistributionChart()}
        {activeChart === 'performance' && renderPerformanceStats()}
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
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: backgroundColor,
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
    fontSize: 14,
    color: secondaryTextColor,
  },
  activeTabText: {
    color: primaryColor,
    fontWeight: '600',
  },
  chartContent: {
    maxHeight: 350, // 设置最大高度，确保有滚动空间
    padding: 16,
  },
  chartContentContainer: {
    flexGrow: 1,
    minHeight: 280, // 设置最小内容高度，确保有足够的内容可以滚动
  },
  emptyText: {
    textAlign: 'center',
    color: secondaryTextColor,
    fontSize: 16,
    padding: 40,
  },
  emptyChart: {
    height: 200,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyChartText: {
    color: secondaryTextColor,
    fontSize: 16,
  },
  chartContainer: {
    marginBottom: 20,
  },
  chart: {
    flexDirection: 'row',
    backgroundColor: backgroundColor,
    borderRadius: 8,
    padding: 10,
    position: 'relative',
  },
  yAxis: {
    width: 50,
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    paddingRight: 10,
    paddingTop: 10,
    paddingBottom: 10,
  },
  axisLabel: {
    fontSize: 11,
    color: secondaryTextColor,
    fontWeight: '500',
    minWidth: 35,
    textAlign: 'right',
  },
  scrollableChart: {
    flex: 1,
  },
  chartArea: {
    position: 'relative',
    height: '100%',
    marginTop: 15,
    marginBottom: 5,
  },
  gridLines: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
  },
  gridLine: {
    position: 'absolute',
    left: 0,
    right: 0,
    height: 1,
    backgroundColor: borderColor,
  },
  dataArea: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
  },
  dataPoint: {
    position: 'absolute',
    width: 8,
    height: 8,
    borderRadius: 4,
    marginLeft: -4,
    marginBottom: -4,
  },
  dataPointText: {
    position: 'absolute',
    top: -25,
    left: -18,
    fontSize: 11,
    color: textColor,
    fontWeight: '600',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    paddingHorizontal: 6,
    paddingVertical: 3,
    borderRadius: 6,
    minWidth: 36,
    textAlign: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  scrollableXAxis: {
    marginTop: 10,
  },
  xAxis: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 60,
  },
  xAxisLabelContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  xAxisLabel: {
    fontSize: 11,
    color: secondaryTextColor,
    textAlign: 'center',
  },
  todayLabel: {
    color: primaryColor,
    fontWeight: '600',
  },
  futureLabel: {
    color: '#999',
    fontStyle: 'italic',
  },
  todayIndicator: {
    fontSize: 8,
    color: primaryColor,
    fontWeight: '600',
    marginTop: 2,
  },
  distributionChart: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'flex-end',
    height: 200,
    paddingHorizontal: 10,
  },
  distributionBar: {
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 2,
  },
  bar: {
    width: '80%',
    minHeight: 10,
    borderRadius: 4,
    justifyContent: 'flex-end',
    alignItems: 'center',
    paddingBottom: 4,
  },
  barValue: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  barLabel: {
    fontSize: 10,
    color: secondaryTextColor,
    marginTop: 8,
    textAlign: 'center',
  },
  performanceContainer: {
    gap: 20,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  statCard: {
    backgroundColor: backgroundColor,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    flex: 1,
    minWidth: '45%',
    borderWidth: 1,
    borderColor: borderColor,
  },
  statValue: {
    fontSize: 24,
    fontWeight: '700',
    color: textColor,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: secondaryTextColor,
    textAlign: 'center',
  },
});

export default LearningAnalytics;
