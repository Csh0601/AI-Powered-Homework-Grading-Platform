import { RouteProp, useNavigation, useRoute } from '@react-navigation/native';
import React from 'react';
import { SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';
import LaTeXRenderer from '../components/LaTeXRenderer';
import { RootStackParamList } from '../navigation/NavigationTypes';
import { cardBackgroundColor, secondaryTextColor, textColor } from '../styles/colors';

type ExplanationRouteProp = RouteProp<RootStackParamList, 'Explanation'>;

const ExplanationScreen: React.FC = () => {
  const route = useRoute<ExplanationRouteProp>();
  const navigation = useNavigation();

  const result = route.params?.result ?? {};

  const hasLaTeX = (text: string): boolean => {
    if (!text) return false;
    return /\frac|\times|\div|\^|_|\\[a-zA-Z]+/.test(text);
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>题目</Text>
          <View style={styles.card}>
            <ScrollView
              style={styles.cardScroll}
              contentContainerStyle={styles.cardScrollContent}
              nestedScrollEnabled
            >
              {hasLaTeX(result.question) ? (
                <LaTeXRenderer content={result.question} fontSize={18} color={textColor} />
              ) : (
                <Text style={styles.text}>{result.question || '题目内容缺失'}</Text>
              )}
            </ScrollView>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>学生答案</Text>
          <View style={styles.card}>
            <ScrollView
              style={styles.cardScroll}
              contentContainerStyle={styles.cardScrollContent}
              nestedScrollEnabled
            >
              {hasLaTeX(result.userAnswer) ? (
                <LaTeXRenderer content={result.userAnswer} fontSize={16} color={textColor} />
              ) : (
                <Text style={styles.text}>{result.userAnswer || '未作答'}</Text>
              )}
            </ScrollView>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>正确答案</Text>
          <View style={styles.card}>
            <ScrollView
              style={styles.cardScroll}
              contentContainerStyle={styles.cardScrollContent}
              nestedScrollEnabled
            >
              {hasLaTeX(result.correctAnswer) ? (
                <LaTeXRenderer content={result.correctAnswer} fontSize={16} color={textColor} />
              ) : (
                <Text style={styles.text}>{result.correctAnswer || '参考答案缺失'}</Text>
              )}
            </ScrollView>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>解析</Text>
          <View style={styles.card}>
            <ScrollView
              style={styles.cardScroll}
              contentContainerStyle={styles.cardScrollContent}
              nestedScrollEnabled
            >
              {hasLaTeX(result.explanation) ? (
                <LaTeXRenderer content={result.explanation} fontSize={15} color={secondaryTextColor} />
              ) : (
                <Text style={[styles.text, styles.detailText]}>
                  {result.explanation || '暂无解析'}
                </Text>
              )}
            </ScrollView>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F5F5FF',
  },
  container: {
    flex: 1,
  },
  contentContainer: {
    padding: 20,
    paddingBottom: 40,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: textColor,
    marginBottom: 12,
  },
  card: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.05)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 3,
    maxHeight: 220,
  },
  text: {
    fontSize: 16,
    color: textColor,
    lineHeight: 24,
  },
  detailText: {
    color: secondaryTextColor,
  },
  cardScroll: {
    maxHeight: 200,
  },
  cardScrollContent: {
    paddingRight: 4,
  },
});

export default ExplanationScreen;

