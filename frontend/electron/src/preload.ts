import { contextBridge, ipcRenderer } from "electron";

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld("electronAPI", {
  // App info
  getAppVersion: () => ipcRenderer.invoke("get-app-version"),

  // Overlay controls
  showOverlay: () => ipcRenderer.invoke("show-overlay"),
  hideOverlay: () => ipcRenderer.invoke("hide-overlay"),
  toggleOverlay: () => ipcRenderer.invoke("toggle-overlay"),
  setOverlayPosition: (x: number, y: number) =>
    ipcRenderer.invoke("set-overlay-position", x, y),

  // Screen info
  getScreenSize: () => ipcRenderer.invoke("get-screen-size"),

  // Audio recording
  startRecording: () => ipcRenderer.invoke("start-recording"),
  stopRecording: () => ipcRenderer.invoke("stop-recording"),
  getAudioDevices: () => ipcRenderer.invoke("get-audio-devices"),

  // Event listeners
  onOverlayToggle: (callback: (visible: boolean) => void) => {
    ipcRenderer.on("overlay-toggled", (event, visible) => callback(visible));
  },

  onRecordingStateChange: (callback: (recording: boolean) => void) => {
    ipcRenderer.on("recording-state-changed", (event, recording) =>
      callback(recording)
    );
  },
});

// Type definitions for the exposed API
export interface ElectronAPI {
  getAppVersion: () => Promise<string>;
  showOverlay: () => Promise<void>;
  hideOverlay: () => Promise<void>;
  toggleOverlay: () => Promise<void>;
  setOverlayPosition: (x: number, y: number) => Promise<void>;
  getScreenSize: () => Promise<{ width: number; height: number }>;
  startRecording: () => Promise<{ success: boolean }>;
  stopRecording: () => Promise<{ success: boolean }>;
  getAudioDevices: () => Promise<any[]>;
  onOverlayToggle: (callback: (visible: boolean) => void) => void;
  onRecordingStateChange: (callback: (recording: boolean) => void) => void;
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}
