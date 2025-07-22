import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import type { CorrectionResult } from '../models/CorrectionResult';

interface ResultItemProps {
  result: CorrectionResult;
}

const ResultItem: React.FC<ResultItemProps> = ({ result }) => {
  return (
    <View style={styles.container}>
      <View style={styles.row}>
        <Text style={styles.title}>题目：</Text>
        <Text style={styles.content}>{result.question}</Text>
      </View>
      <View style={styles.row}>
        <Text style={styles.title}>你的答案：</Text>
        <Text style={styles.content}>{result.userAnswer}</Text>
      </View>
      <View style={styles.row}>
        <Text style={styles.title}>正确答案：</Text>
        <Text style={styles.content}>{result.correctAnswer}</Text>
      </View>
      <View style={styles.row}>
        <Text style={styles.title}>知识点：</Text>
        <Text style={styles.content}>{result.knowledgePoint}</Text>
      </View>
      <View style={styles.row}>
        <Text style={styles.title}>判定：</Text>
        <Text style={[styles.judge, result.isCorrect ? styles.correct : styles.incorrect]}>
          {result.isCorrect ? '✔ 正确' : '✘ 错误'}
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#f8f8f8',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
    elevation: 2,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  title: {
    fontWeight: 'bold',
    minWidth: 80,
    color: '#333',
  },
  content: {
    flex: 1,
    color: '#444',
  },
  judge: {
    fontWeight: 'bold',
    fontSize: 16,
    marginLeft: 8,
  },
  correct: {
    color: '#4CAF50',
  },
  incorrect: {
    color: '#F44336',
  },
});

export default ResultItem;
