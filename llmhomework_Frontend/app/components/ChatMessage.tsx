/**
 * 聊天消息气泡组件 - iMessage 风格
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import type { ChatMessage as ChatMessageType } from '../models/Chat';
import {
  primaryColor,
  textPrimary,
  textSecondary,
  cardBackground,
  borderColor,
  textInverse,
  primaryAlpha10
} from '../styles/colors';
import { typography, spacing, borderRadius } from '../styles/designSystem';

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
    marginVertical: spacing.xs,
    marginHorizontal: spacing.md,
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
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: primaryAlpha10,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: spacing.sm,
  },
  avatarText: {
    fontSize: 18,
  },
  messageBubble: {
    flex: 1,
    borderRadius: borderRadius.lg,  // iMessage 圆角
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    // 移除阴影，保持 Apple 简洁风格
  },
  userBubble: {
    backgroundColor: primaryColor,  // iOS Blue
    borderBottomRightRadius: spacing.xs,  // iMessage 尾巴
  },
  aiBubble: {
    backgroundColor: cardBackground,  // 浅灰色背景
    borderBottomLeftRadius: spacing.xs,  // iMessage 尾巴
    borderWidth: 0.5,  // Apple 精细边框
    borderColor: borderColor,
  },
  messageText: {
    ...typography.bodyMedium,
    lineHeight: 21,
  },
  userText: {
    color: textInverse,  // 白色文字
  },
  aiText: {
    color: textPrimary,
  },
  timestamp: {
    ...typography.caption,
    marginTop: spacing.xs,
  },
  userTimestamp: {
    color: 'rgba(255, 255, 255, 0.7)',
    textAlign: 'right',
  },
  aiTimestamp: {
    color: textSecondary,
    textAlign: 'left',
  },
  systemMessageContainer: {
    alignSelf: 'center',
    marginVertical: spacing.sm,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.xs,
    backgroundColor: primaryAlpha10,
    borderRadius: borderRadius.md,
  },
  systemMessageText: {
    ...typography.caption,
    color: textSecondary,
    textAlign: 'center',
  },
});

export default ChatMessage;
