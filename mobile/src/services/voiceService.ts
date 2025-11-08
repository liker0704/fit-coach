import { Audio } from 'expo-av';
import { apiClient } from './api/apiClient';
import { getToken } from './api/authService';

export interface TranscriptionResult {
  success: boolean;
  text: string;
  language?: string;
}

export interface TTSResult {
  success: boolean;
  audio_base64: string;
  format: string;
}

export class VoiceService {
  private static recording: Audio.Recording | null = null;
  private static sound: Audio.Sound | null = null;

  /**
   * Request audio recording permissions
   */
  static async requestPermissions(): Promise<boolean> {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('Error requesting audio permissions:', error);
      return false;
    }
  }

  /**
   * Start recording audio
   */
  static async startRecording(): Promise<void> {
    try {
      // Request permissions
      const hasPermission = await this.requestPermissions();
      if (!hasPermission) {
        throw new Error('Audio recording permission not granted');
      }

      // Set audio mode for recording
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      // Create recording instance
      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );

      this.recording = recording;
    } catch (error) {
      console.error('Error starting recording:', error);
      throw error;
    }
  }

  /**
   * Stop recording and return the audio URI
   */
  static async stopRecording(): Promise<string | null> {
    try {
      if (!this.recording) {
        return null;
      }

      await this.recording.stopAndUnloadAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
      });

      const uri = this.recording.getURI();
      this.recording = null;

      return uri;
    } catch (error) {
      console.error('Error stopping recording:', error);
      throw error;
    }
  }

  /**
   * Convert audio to text using backend API (OpenAI Whisper)
   */
  static async speechToText(
    audioUri: string,
    language: string = 'en'
  ): Promise<TranscriptionResult> {
    try {
      const token = await getToken();
      const baseURL = apiClient.defaults.baseURL || '';

      // Create form data
      const formData = new FormData();

      // Extract file info from URI
      const filename = audioUri.split('/').pop() || 'recording.m4a';
      const match = /\.(\w+)$/.exec(filename);
      const type = match ? `audio/${match[1]}` : 'audio/m4a';

      // @ts-ignore - React Native FormData accepts URI
      formData.append('audio', {
        uri: audioUri,
        name: filename,
        type,
      });

      formData.append('language', language);

      // Send to backend
      const response = await fetch(`${baseURL}/voice/speech-to-text`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error in speech-to-text:', error);
      throw error;
    }
  }

  /**
   * Convert text to speech using backend API (OpenAI TTS)
   */
  static async textToSpeech(
    text: string,
    voice: string = 'alloy',
    speed: number = 1.0
  ): Promise<TTSResult> {
    try {
      const response = await apiClient.post('/voice/text-to-speech', {
        text,
        voice,
        speed,
      });

      return response.data;
    } catch (error) {
      console.error('Error in text-to-speech:', error);
      throw error;
    }
  }

  /**
   * Play audio from base64 string
   */
  static async playAudio(base64Audio: string): Promise<void> {
    try {
      // Unload previous sound if exists
      if (this.sound) {
        await this.sound.unloadAsync();
        this.sound = null;
      }

      // Set audio mode for playback
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: true,
        playThroughEarpieceAndroid: false,
      });

      // Create sound from base64
      const { sound } = await Audio.Sound.createAsync(
        { uri: `data:audio/mp3;base64,${base64Audio}` },
        { shouldPlay: true }
      );

      this.sound = sound;

      // Auto-unload when finished
      sound.setOnPlaybackStatusUpdate((status) => {
        if (status.isLoaded && status.didJustFinish) {
          sound.unloadAsync();
          this.sound = null;
        }
      });
    } catch (error) {
      console.error('Error playing audio:', error);
      throw error;
    }
  }

  /**
   * Stop currently playing audio
   */
  static async stopAudio(): Promise<void> {
    try {
      if (this.sound) {
        await this.sound.stopAsync();
        await this.sound.unloadAsync();
        this.sound = null;
      }
    } catch (error) {
      console.error('Error stopping audio:', error);
    }
  }

  /**
   * Check if currently recording
   */
  static isRecording(): boolean {
    return this.recording !== null;
  }

  /**
   * Check if currently playing audio
   */
  static async isPlaying(): Promise<boolean> {
    if (!this.sound) {
      return false;
    }

    try {
      const status = await this.sound.getStatusAsync();
      return status.isLoaded && status.isPlaying;
    } catch (error) {
      return false;
    }
  }
}
