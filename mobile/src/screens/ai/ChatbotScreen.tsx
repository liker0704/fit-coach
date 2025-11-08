import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import {
  Text,
  TextInput,
  IconButton,
  Card,
  ActivityIndicator,
} from 'react-native-paper';
import { colors, spacing, fontSizes } from '../../theme/colors';
import { agentService, ChatMessage } from '../../services/api/agentService';

export default function ChatbotScreen() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content:
        'Hello! I\'m your FitCoach AI assistant. How can I help you today?',
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);

  // Auto-scroll to bottom when new message added
  useEffect(() => {
    scrollViewRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  const handleSend = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await agentService.sendChatMessage(inputText);

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);

      const errorMessage: ChatMessage = {
        role: 'assistant',
        content:
          'Sorry, I encountered an error. Please try again or check your connection.',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={100}
    >
      {/* Messages */}
      <ScrollView
        ref={scrollViewRef}
        style={styles.messagesContainer}
        contentContainerStyle={styles.messagesContent}
      >
        {messages.map((message, index) => (
          <View
            key={index}
            style={[
              styles.messageWrapper,
              message.role === 'user'
                ? styles.userMessageWrapper
                : styles.assistantMessageWrapper,
            ]}
          >
            <Card
              style={[
                styles.messageCard,
                message.role === 'user'
                  ? styles.userMessage
                  : styles.assistantMessage,
              ]}
            >
              <Card.Content>
                <Text
                  style={[
                    styles.messageText,
                    message.role === 'user' && styles.userMessageText,
                  ]}
                >
                  {message.content}
                </Text>
                <Text
                  style={[
                    styles.timestamp,
                    message.role === 'user' && styles.userTimestamp,
                  ]}
                >
                  {message.timestamp.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </Text>
              </Card.Content>
            </Card>
          </View>
        ))}

        {isLoading && (
          <View style={styles.loadingWrapper}>
            <Card style={styles.loadingCard}>
              <Card.Content style={styles.loadingContent}>
                <ActivityIndicator size="small" color={colors.primary} />
                <Text style={styles.loadingText}>Thinking...</Text>
              </Card.Content>
            </Card>
          </View>
        )}
      </ScrollView>

      {/* Input */}
      <View style={styles.inputContainer}>
        <TextInput
          value={inputText}
          onChangeText={setInputText}
          placeholder="Type your message..."
          mode="outlined"
          style={styles.input}
          multiline
          maxLength={500}
          onSubmitEditing={handleSend}
          disabled={isLoading}
        />
        <IconButton
          icon="send"
          size={24}
          iconColor={colors.primary}
          onPress={handleSend}
          disabled={!inputText.trim() || isLoading}
          style={styles.sendButton}
        />
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: spacing.md,
    paddingBottom: spacing.xl,
  },
  messageWrapper: {
    marginBottom: spacing.md,
    maxWidth: '80%',
  },
  userMessageWrapper: {
    alignSelf: 'flex-end',
  },
  assistantMessageWrapper: {
    alignSelf: 'flex-start',
  },
  messageCard: {
    elevation: 1,
  },
  userMessage: {
    backgroundColor: colors.primary,
  },
  assistantMessage: {
    backgroundColor: colors.backgroundSecondary,
  },
  messageText: {
    fontSize: fontSizes.md,
    color: colors.text,
    lineHeight: 22,
  },
  userMessageText: {
    color: colors.background,
  },
  timestamp: {
    fontSize: fontSizes.xs,
    color: colors.textTertiary,
    marginTop: spacing.xs,
  },
  userTimestamp: {
    color: 'rgba(255, 255, 255, 0.7)',
  },
  loadingWrapper: {
    alignSelf: 'flex-start',
    maxWidth: '80%',
  },
  loadingCard: {
    backgroundColor: colors.backgroundSecondary,
    elevation: 1,
  },
  loadingContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  loadingText: {
    marginLeft: spacing.sm,
    fontSize: fontSizes.md,
    color: colors.textSecondary,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: spacing.md,
    backgroundColor: colors.background,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  input: {
    flex: 1,
    marginRight: spacing.sm,
    maxHeight: 100,
  },
  sendButton: {
    margin: 0,
  },
});
