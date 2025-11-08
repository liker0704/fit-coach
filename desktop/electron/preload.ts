import { contextBridge, ipcRenderer } from 'electron';

interface NotificationSettings {
  enabled: boolean;
  reminderTime: string;
}

// Expose Electron APIs to renderer process
contextBridge.exposeInMainWorld('electron', {
  notifications: {
    updateSettings: (settings: NotificationSettings) =>
      ipcRenderer.invoke('notifications:update-settings', settings),
    getSettings: () =>
      ipcRenderer.invoke('notifications:get-settings'),
    test: () =>
      ipcRenderer.invoke('notifications:test'),
  },
});
