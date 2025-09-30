// 知识点卡片组件
import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { 
  primaryColor, 
  successColor, 
  warningColor,
  textColor, 
  secondaryTextColor, 
  cardBackgroundColor,
  borderColor,
  backgroundColor 
} from '../styles/colors';

interface KnowledgePointsCardProps {
  knowledgePoints: string[];
  title?: string;
  maxHeight?: number;
}

const KnowledgePointsCard: React.FC<KnowledgePointsCardProps> = ({
  knowledgePoints,
  title = "涉及知识点",
  maxHeight = 200
}) => {
  if (!knowledgePoints || knowledgePoints.length === 0) {
    return null;
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerIcon}>🧠</Text>
        <Text style={styles.title}>{title}</Text>
        <View style={styles.countBadge}>
          <Text style={styles.countText}>{knowledgePoints.length}</Text>
        </View>
      </View>
      
      <ScrollView 
        style={[styles.scrollContainer, { maxHeight }]}
        showsVerticalScrollIndicator={true}
        nestedScrollEnabled={true}
      >
        <View style={styles.pointsContainer}>
          {knowledgePoints.map((point, index) => (
            <View key={index} style={styles.pointItem}>
              <View style={styles.pointDot} />
              <Text style={styles.pointText}>{point}</Text>
            </View>
          ))}
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
    backgroundColor: primaryColor,
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
  pointsContainer: {
    gap: 8,
  },
  pointItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingVertical: 4,
  },
  pointDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: primaryColor,
    marginTop: 6,
    marginRight: 10,
    flexShrink: 0,
  },
  pointText: {
    fontSize: 14,
    color: textColor,
    lineHeight: 20,
    flex: 1,
  },
});

export default KnowledgePointsCard;
