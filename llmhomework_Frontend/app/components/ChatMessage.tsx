/**
 * 聊天消息气泡组件
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import type { ChatMessage as ChatMessageType } from '../models/Chat';
import { primaryColor, secondaryColor, textColor, secondaryTextColor, cardBackgroundColor, systemGray6 } from '../styles/colors';

interface ChatMessageProps {
  message: ChatMessageType;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  // 格式化时间戳
  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const hours = date.getHours().toString().padStart(2, '0');
      const minutes = date.getMinutes().toString().padStart(2, '0');
      return `${hours}:${minutes}`;
    } catch {
      return '';
    }
  };

  if (isSystem) {
    // 系统消息（居中显示）
    return (
      <View style={styles.systemMessageContainer}>
        <Text style={styles.systemMessageText}>{message.content}</Text>
      </View>
    );
  }

  return (
    <View style={[
      styles.messageContainer,
      isUser ? styles.userMessageContainer : styles.aiMessageContainer
    ]}>
      {/* AI消息显示头像 */}
      {!isUser && (
        <View style={styles.avatarContainer}>
          <Text style={styles.avatarText}>🤖</Text>
        </View>
      )}

      <View style={[
        styles.messageBubble,
        isUser ? styles.userBubble : styles.aiBubble
      ]}>
        <Text style={[
          styles.messageText,
          isUser ? styles.userText : styles.aiText
        ]}>
          {message.content}
        </Text>
        
        {/* 时间戳 */}
        <Text style={[
          styles.timestamp,
          isUser ? styles.userTimestamp : styles.aiTimestamp
        ]}>
          {formatTime(message.timestamp)}
        </Text>
      </View>

      {/* 用户消息显示头像 */}
      {isUser && (
        <View style={styles.avatarContainer}>
          <Text style={styles.avatarText}>👤</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  messageContainer: {
    flexDirection: 'row',
    marginVertical: 4,
    marginHorizontal: 12,
    maxWidth: '85%',
  },
  userMessageContainer: {
    alignSelf: 'flex-end',
    flexDirection: 'row-reverse',
  },
  aiMessageContainer: {
    alignSelf: 'flex-start',
  },
  avatarContainer: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: systemGray6,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 8,
  },
  avatarText: {
    fontSize: 20,
  },
  messageBubble: {
    flex: 1,
    borderRadius: 16,
    paddingHorizontal: 14,
    paddingVertical: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  userBubble: {
    backgroundColor: primaryColor,
    borderBottomRightRadius: 4,
  },
  aiBubble: {
    backgroundColor: cardBackgroundColor,
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: systemGray6,
  },
  messageText: {
    fontSize: 15,
    lineHeight: 21,
  },
  userText: {
    color: '#FFFFFF',
  },
  aiText: {
    color: textColor,
  },
  timestamp: {
    fontSize: 11,
    marginTop: 4,
  },
  userTimestamp: {
    color: 'rgba(255, 255, 255, 0.7)',
    textAlign: 'right',
  },
  aiTimestamp: {
    color: secondaryTextColor,
    textAlign: 'left',
  },
  systemMessageContainer: {
    alignSelf: 'center',
    marginVertical: 8,
    paddingHorizontal: 16,
    paddingVertical: 6,
    backgroundColor: 'rgba(0, 0, 0, 0.05)',
    borderRadius: 12,
  },
  systemMessageText: {
    fontSize: 12,
    color: secondaryTextColor,
    textAlign: 'center',
  },
});

export default ChatMessage;
