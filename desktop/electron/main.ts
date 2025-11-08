import { app, BrowserWindow, shell, Notification, ipcMain } from 'electron';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const isDev = process.env.NODE_ENV === 'development';

// Notification settings
interface NotificationSettings {
  enabled: boolean;
  reminderTime: string; // Format: "HH:MM"
}

let notificationSettings: NotificationSettings = {
  enabled: false,
  reminderTime: '21:00',
};

let dailyReminderInterval: NodeJS.Timeout | null = null;

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    title: 'FitCoach Desktop',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  // Remove menu bar (File, Edit, View, Window, Help)
  mainWindow.setMenu(null);

  if (isDev) {
    mainWindow.loadURL('http://localhost:1420');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  // Handle external links (replaces tauri-plugin-opener)
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Notification functions
function showNotification(title: string, body: string) {
  if (Notification.isSupported()) {
    const notification = new Notification({
      title,
      body,
      icon: path.join(__dirname, '../public/icon.png'), // Optional: add app icon
    });
    notification.show();
  }
}

function scheduleDailyReminder() {
  // Clear existing interval if any
  if (dailyReminderInterval) {
    clearInterval(dailyReminderInterval);
  }

  if (!notificationSettings.enabled) {
    return;
  }

  // Check every minute if it's time to send reminder
  dailyReminderInterval = setInterval(() => {
    const now = new Date();
    const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;

    if (currentTime === notificationSettings.reminderTime) {
      showNotification(
        'FitCoach Daily Reminder',
        "Don't forget to log your day! Track your meals, exercise, and health metrics."
      );
    }
  }, 60000); // Check every minute
}

// IPC Handlers
ipcMain.handle('notifications:update-settings', (_event, settings: NotificationSettings) => {
  notificationSettings = settings;
  scheduleDailyReminder();
  return { success: true };
});

ipcMain.handle('notifications:get-settings', () => {
  return notificationSettings;
});

ipcMain.handle('notifications:test', () => {
  showNotification(
    'FitCoach Test Notification',
    'Notifications are working! You will receive daily reminders at your set time.'
  );
  return { success: true };
});

// Request notification permission on app ready
app.whenReady().then(() => {
  // Initialize notification scheduling
  scheduleDailyReminder();
});
