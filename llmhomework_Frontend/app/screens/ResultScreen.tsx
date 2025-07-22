import { RouteProp, useRoute } from '@react-navigation/native';
import React from 'react';
import { FlatList, StyleSheet, Text, View } from 'react-native';
import ResultItem from '../components/ResultItem';
import { CorrectionResult } from '../models/CorrectionResult';
import { RootStackParamList } from '../navigation/NavigationTypes';

// 路由类型

type ResultScreenRouteProp = RouteProp<RootStackParamList, 'Result'>;

const ResultScreen: React.FC = () => {
  const route = useRoute<ResultScreenRouteProp>();
  const gradingResult = route.params?.gradingResult || [];
  const wrongKnowledges = route.params?.wrongKnowledges || [];
  const history = route.params?.history || [];

  return (
    <View style={styles.container}>
      <Text style={styles.title}>批改结果</Text>
      <FlatList
        data={gradingResult}
        keyExtractor={(_, idx) => idx.toString()}
        renderItem={({ item }) => <ResultItem result={item as CorrectionResult} />}
        contentContainerStyle={styles.list}
      />
      <Text style={styles.title}>错题知识点分析</Text>
      <Text>{wrongKnowledges.length ? wrongKnowledges.join('、') : '无错题'}</Text>
      {history.length > 0 && (
        <>
          <Text style={styles.title}>历史记录</Text>
          <FlatList
            data={history}
            keyExtractor={(_, idx) => idx.toString()}
            renderItem={({ item }) => <Text>{JSON.stringify(item)}</Text>}
          />
        </>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    marginVertical: 10,
  },
  list: {
    marginBottom: 20,
  },
});

export default ResultScreen;
