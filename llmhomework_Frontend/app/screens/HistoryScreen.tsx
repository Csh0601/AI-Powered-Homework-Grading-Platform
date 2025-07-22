import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Alert, FlatList, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { RootStackParamList } from '../navigation/NavigationTypes';
import historyService from '../services/historyService';

interface HistoryRecord {
  id: string;
  date: string;
  summary: string;
}

type HistoryScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'History'>;

const HistoryScreen: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const navigation = useNavigation<HistoryScreenNavigationProp>();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await historyService.loadHistory();
        setRecords(data);
      } catch (error: any) {
        Alert.alert('加载失败', error.message || '未知错误');
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const handlePress = (id: string) => {
    navigation.navigate('Result', { resultId: id });
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#4CAF50" />
        <Text style={{ marginTop: 10 }}>正在加载历史记录...</Text>
      </View>
    );
  }

  if (!records.length) {
    return (
      <View style={styles.center}>
        <Text>暂无历史记录</Text>
      </View>
    );
  }

  return (
    <FlatList
      data={records}
      keyExtractor={item => item.id}
      renderItem={({ item }) => (
        <TouchableOpacity style={styles.item} onPress={() => handlePress(item.id)}>
          <Text style={styles.date}>{item.date}</Text>
          <Text style={styles.summary}>{item.summary}</Text>
        </TouchableOpacity>
      )}
      contentContainerStyle={styles.list}
    />
  );
};

const styles = StyleSheet.create({
  center: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
  },
  list: {
    padding: 16,
    backgroundColor: '#fff',
  },
  item: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    backgroundColor: '#fafafa',
    borderRadius: 8,
    marginBottom: 10,
  },
  date: {
    fontSize: 14,
    color: '#888',
    marginBottom: 4,
  },
  summary: {
    fontSize: 16,
    color: '#222',
  },
});

export default HistoryScreen;
