export interface NotificationSettings {
  enabled: boolean;
  reminderTime: string;
}

export interface ElectronAPI {
  notifications: {
    updateSettings: (settings: NotificationSettings) => Promise<{ success: boolean }>;
    getSettings: () => Promise<NotificationSettings>;
    test: () => Promise<{ success: boolean }>;
  };
}

declare global {
  interface Window {
    electron?: ElectronAPI;
  }
}

export {};
