import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Alert } from 'react-native';
import ChatbotScreen from '../ai/ChatbotScreen';
import { agentService } from '../../services/api/agentService';
import { VoiceService } from '../../services/voiceService';

jest.mock('../../services/api/agentService');
jest.mock('../../services/voiceService');

const mockedAgentService = agentService as jest.Mocked<typeof agentService>;
const mockedVoiceService = VoiceService as jest.Mocked<typeof VoiceService>;

describe('ChatbotScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(Alert, 'alert').mockImplementation();
  });

  it('should render chatbot screen with initial message', () => {
    const { getByText } = render(<ChatbotScreen />);

    expect(
      getByText("Hello! I'm your FitCoach AI assistant. How can I help you today?")
    ).toBeTruthy();
  });

  it('should render text input for messages', () => {
    const { getByPlaceholderText } = render(<ChatbotScreen />);

    const input = getByPlaceholderText(/type.*message/i);
    expect(input).toBeTruthy();
  });

  it('should send message when send button pressed', async () => {
    mockedAgentService.streamChatMessage = jest.fn((message, onChunk, onComplete) => {
      onChunk('AI response');
      onComplete();
      return Promise.resolve();
    });

    const { getByPlaceholderText, getByTestId } = render(<ChatbotScreen />);

    const input = getByPlaceholderText(/type.*message/i);
    const sendButton = getByTestId('send-button') || getByPlaceholderText(/send/i);

    fireEvent.changeText(input, 'What should I eat today?');
    fireEvent.press(sendButton);

    await waitFor(() => {
      expect(mockedAgentService.streamChatMessage).toHaveBeenCalled();
    });
  });

  it('should not send empty message', () => {
    const { getByPlaceholderText, getByTestId } = render(<ChatbotScreen />);

    const input = getByPlaceholderText(/type.*message/i);
    const sendButton = getByTestId('send-button') || getByPlaceholderText(/send/i);

    fireEvent.changeText(input, '   ');
    fireEvent.press(sendButton);

    expect(mockedAgentService.streamChatMessage).not.toHaveBeenCalled();
  });

  it('should clear input after sending message', async () => {
    mockedAgentService.streamChatMessage = jest.fn((message, onChunk, onComplete) => {
      onChunk('Response');
      onComplete();
      return Promise.resolve();
    });

    const { getByPlaceholderText, getByTestId } = render(<ChatbotScreen />);

    const input = getByPlaceholderText(/type.*message/i);
    const sendButton = getByTestId('send-button') || getByPlaceholderText(/send/i);

    fireEvent.changeText(input, 'Test message');
    fireEvent.press(sendButton);

    await waitFor(() => {
      expect(input.props.value).toBe('');
    });
  });

  it('should handle voice input start', async () => {
    mockedVoiceService.startRecording = jest.fn().mockResolvedValue(undefined);

    const { getByTestId } = render(<ChatbotScreen />);

    const voiceButton = getByTestId('voice-button');
    fireEvent.press(voiceButton);

    await waitFor(() => {
      expect(mockedVoiceService.startRecording).toHaveBeenCalled();
    });
  });

  it('should handle voice input stop and transcription', async () => {
    mockedVoiceService.stopRecording = jest
      .fn()
      .mockResolvedValue('audio-uri.m4a');
    mockedVoiceService.speechToText = jest.fn().mockResolvedValue({
      success: true,
      text: 'Transcribed text from voice',
    });

    const { getByTestId, getByPlaceholderText } = render(<ChatbotScreen />);

    const voiceButton = getByTestId('voice-button');

    // Start recording
    mockedVoiceService.startRecording = jest.fn().mockResolvedValue(undefined);
    fireEvent.press(voiceButton);

    await waitFor(() => {
      expect(mockedVoiceService.startRecording).toHaveBeenCalled();
    });

    // Stop recording
    fireEvent.press(voiceButton);

    await waitFor(() => {
      expect(mockedVoiceService.stopRecording).toHaveBeenCalled();
      expect(mockedVoiceService.speechToText).toHaveBeenCalledWith('audio-uri.m4a');
    });

    const input = getByPlaceholderText(/type.*message/i);
    expect(input.props.value).toBe('Transcribed text from voice');
  });

  it('should show error alert on voice transcription failure', async () => {
    mockedVoiceService.stopRecording = jest
      .fn()
      .mockResolvedValue('audio-uri.m4a');
    mockedVoiceService.speechToText = jest.fn().mockResolvedValue({
      success: false,
      text: null,
    });

    const { getByTestId } = render(<ChatbotScreen />);

    const voiceButton = getByTestId('voice-button');

    mockedVoiceService.startRecording = jest.fn().mockResolvedValue(undefined);
    fireEvent.press(voiceButton);

    await waitFor(() => {
      expect(mockedVoiceService.startRecording).toHaveBeenCalled();
    });

    fireEvent.press(voiceButton);

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith('Error', 'Failed to transcribe audio');
    });
  });

  it('should display user and assistant messages', async () => {
    mockedAgentService.streamChatMessage = jest.fn((message, onChunk, onComplete) => {
      onChunk('This is the AI response');
      onComplete();
      return Promise.resolve();
    });

    const { getByPlaceholderText, getByTestId, getByText } = render(
      <ChatbotScreen />
    );

    const input = getByPlaceholderText(/type.*message/i);
    const sendButton = getByTestId('send-button') || getByPlaceholderText(/send/i);

    fireEvent.changeText(input, 'User question');
    fireEvent.press(sendButton);

    await waitFor(() => {
      expect(getByText('User question')).toBeTruthy();
      expect(getByText('This is the AI response')).toBeTruthy();
    });
  });

  it('should handle streaming error gracefully', async () => {
    mockedAgentService.streamChatMessage = jest.fn(
      (message, onChunk, onComplete, onError) => {
        onError(new Error('Streaming error'));
        return Promise.resolve();
      }
    );

    const { getByPlaceholderText, getByTestId } = render(<ChatbotScreen />);

    const input = getByPlaceholderText(/type.*message/i);
    const sendButton = getByTestId('send-button') || getByPlaceholderText(/send/i);

    fireEvent.changeText(input, 'Test message');
    fireEvent.press(sendButton);

    await waitFor(() => {
      expect(mockedAgentService.streamChatMessage).toHaveBeenCalled();
    });
  });
});
