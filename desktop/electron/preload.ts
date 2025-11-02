import { contextBridge } from 'electron';

// Minimal preload - app uses standard web APIs (axios, localStorage, React Router)
// No custom IPC needed as there was no Tauri IPC in the original code
contextBridge.exposeInMainWorld('electron', {
  // Placeholder for future Electron-specific APIs if needed
});
