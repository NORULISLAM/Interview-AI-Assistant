import { create } from "zustand";

interface SessionState {
  currentSessionId: number | null;
  isRecording: boolean;
  isOverlayVisible: boolean;
  transcript: string[];
  suggestions: any[];
  isConnected: boolean;
}

interface SessionActions {
  startSession: (sessionId: number) => Promise<void>;
  stopSession: () => void;
  toggleRecording: () => void;
  toggleOverlay: () => void;
  addTranscriptSegment: (text: string) => void;
  addSuggestion: (suggestion: any) => void;
  clearTranscript: () => void;
  setConnectionStatus: (connected: boolean) => void;
}

type SessionStore = SessionState & SessionActions;

export const useSessionStore = create<SessionStore>((set, get) => ({
  // State
  currentSessionId: null,
  isRecording: false,
  isOverlayVisible: false,
  transcript: [],
  suggestions: [],
  isConnected: false,

  // Actions
  startSession: async (sessionId: number) => {
    set({
      currentSessionId: sessionId,
      isRecording: true,
      transcript: [],
      suggestions: [],
    });

    // TODO: Initialize WebSocket connection
    // TODO: Start audio recording
    console.log("Session started:", sessionId);
  },

  stopSession: () => {
    set({
      currentSessionId: null,
      isRecording: false,
      transcript: [],
      suggestions: [],
    });

    // TODO: Close WebSocket connection
    // TODO: Stop audio recording
    console.log("Session stopped");
  },

  toggleRecording: () => {
    const { isRecording } = get();
    set({ isRecording: !isRecording });

    if (isRecording) {
      // TODO: Stop recording
      console.log("Recording stopped");
    } else {
      // TODO: Start recording
      console.log("Recording started");
    }
  },

  toggleOverlay: () => {
    const { isOverlayVisible } = get();
    set({ isOverlayVisible: !isOverlayVisible });

    // TODO: Communicate with Electron main process
    if (window.electronAPI) {
      if (isOverlayVisible) {
        window.electronAPI.hideOverlay();
      } else {
        window.electronAPI.showOverlay();
      }
    }
  },

  addTranscriptSegment: (text: string) => {
    const { transcript } = get();
    set({ transcript: [...transcript, text] });
  },

  addSuggestion: (suggestion: any) => {
    const { suggestions } = get();
    set({ suggestions: [...suggestions, suggestion] });
  },

  clearTranscript: () => {
    set({ transcript: [] });
  },

  setConnectionStatus: (connected: boolean) => {
    set({ isConnected: connected });
  },
}));
