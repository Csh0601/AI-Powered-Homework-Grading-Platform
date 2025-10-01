/**
 * AI学习伙伴对话界面
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  ActivityIndicator,
  SafeAreaView,
  Alert,
  TouchableOpacity,
} from 'react-native';
import { RouteProp, useRoute, useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { Ionicons } from '@expo/vector-icons';
import ChatMessage from '../components/ChatMessage';
import ChatInput from '../components/ChatInput';
import { chatService } from '../services/chatService';
import type { ChatMessage as ChatMessageType } from '../models/Chat';
import type { RootStackParamList } from '../navigation/NavigationTypes';
import {
  primaryColor,
  backgroundColor,
  textColor,
  secondaryTextColor,
  cardBackgroundColor,
} from '../styles/colors';

type ChatScreenRouteProp = RouteProp<RootStackParamList, 'Chat'>;
type ChatScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Chat'>;

const ChatScreen: React.FC = () => {
  const route = useRoute<ChatScreenRouteProp>();
  const navigation = useNavigation<ChatScreenNavigationProp>();
  const { taskId, gradingResult } = route.params;

  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const flatListRef = useRef<FlatList>(null);

  // 初始化对话
  useEffect(() => {
    initConversation();
  }, []);

  // 设置导航头部
  useEffect(() => {
    navigation.setOptions({
      headerTitle: 'AI学习伙伴',
      headerLeft: () => (
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.headerButton}
        >
          <Ionicons name="arrow-back" size={24} color={primaryColor} />
        </TouchableOpacity>
      ),
    });
  }, [navigation]);

  const initConversation = async () => {
    try {
      setIsInitializing(true);
      setError(null);

      console.log('🚀 初始化对话:', taskId);

      const result = await chatService.startConversation(taskId, gradingResult);

      if (result.success) {
        setConversationId(result.conversation_id);

        // 添加欢迎消息
        const welcomeMessage: ChatMessageType = {
          role: 'assistant',
          content: result.welcome_message,
          timestamp: new Date().toISOString(),
        };
        setMessages([welcomeMessage]);

        console.log('✅ 对话初始化成功');
      } else {
        throw new Error(result.error || '创建对话失败');
      }
    } catch (error: any) {
      console.error('❌ 初始化对话失败:', error);
      setError(error.message || '初始化失败，请重试');
      
      Alert.alert(
        '初始化失败',
        error.message || '无法连接到AI服务，请检查网络后重试',
        [
          { text: '返回', onPress: () => navigation.goBack() },
          { text: '重试', onPress: () => initConversation() },
        ]
      );
    } finally {
      setIsInitializing(false);
    }
  };

  const handleSendMessage = async (userMessage: string) => {
    if (!conversationId || !userMessage.trim()) return;

    // 添加用户消息到界面
    const newUserMessage: ChatMessageType = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, newUserMessage]);
    setIsLoading(true);

    // 滚动到底部
    setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 100);

    try {
      console.log('💬 发送消息:', userMessage);

      const result = await chatService.sendMessage(conversationId, userMessage);

      if (result.success) {
        // 添加AI回复到界面
        const aiMessage: ChatMessageType = {
          role: 'assistant',
          content: result.response,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, aiMessage]);

        // 滚动到底部
        setTimeout(() => {
          flatListRef.current?.scrollToEnd({ animated: true });
        }, 100);

        console.log('✅ 收到AI回复');
      } else {
        throw new Error(result.error || '发送失败');
      }
    } catch (error: any) {
      console.error('❌ 发送消息失败:', error);

      // 添加错误提示消息
      const errorMessage: ChatMessageType = {
        role: 'system',
        content: `发送失败: ${error.message || '请检查网络连接'}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);

      Alert.alert('发送失败', error.message || '请检查网络连接后重试');
    } finally {
      setIsLoading(false);
    }
  };

  // 加载中界面
  if (isInitializing) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={primaryColor} />
          <Text style={styles.loadingText}>正在连接AI学习伙伴...</Text>
        </View>
      </SafeAreaView>
    );
  }

  // 错误界面
  if (error && !conversationId) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle-outline" size={64} color="#FF6B6B" />
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={initConversation}>
            <Text style={styles.retryButtonText}>重试</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.backButtonText}>返回</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  // 正常对话界面
  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.keyboardAvoidingView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        {/* 消息列表 */}
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={({ item }) => <ChatMessage message={item} />}
          keyExtractor={(item, index) => `${index}-${item.timestamp}`}
          contentContainerStyle={styles.messageList}
          onContentSizeChange={() => {
            flatListRef.current?.scrollToEnd({ animated: true });
          }}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>开始和AI聊天吧！</Text>
            </View>
          }
        />

        {/* 加载指示器 */}
        {isLoading && (
          <View style={styles.loadingIndicator}>
            <ActivityIndicator size="small" color={primaryColor} />
            <Text style={styles.loadingIndicatorText}>AI正在思考...</Text>
          </View>
        )}

        {/* 输入框 */}
        <ChatInput
          onSend={handleSendMessage}
          disabled={isLoading || !conversationId}
          placeholder={
            isLoading
              ? 'AI正在思考...'
              : !conversationId
              ? '连接中...'
              : '输入你的问题...'
          }
        />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: backgroundColor,
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  messageList: {
    paddingVertical: 12,
    flexGrow: 1,
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
    padding: 24,
  },
  errorText: {
    marginTop: 16,
    fontSize: 16,
    color: textColor,
    textAlign: 'center',
  },
  retryButton: {
    marginTop: 24,
    paddingHorizontal: 32,
    paddingVertical: 12,
    backgroundColor: primaryColor,
    borderRadius: 24,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  backButton: {
    marginTop: 12,
    paddingHorizontal: 32,
    paddingVertical: 12,
  },
  backButtonText: {
    color: primaryColor,
    fontSize: 16,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    fontSize: 16,
    color: secondaryTextColor,
  },
  loadingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    backgroundColor: cardBackgroundColor,
  },
  loadingIndicatorText: {
    marginLeft: 8,
    fontSize: 14,
    color: secondaryTextColor,
  },
  headerButton: {
    padding: 8,
  },
});

export default ChatScreen;
