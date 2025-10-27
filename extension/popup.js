// Popup script for Interview AI Assistant extension

class PopupManager {
    constructor() {
        this.isConnected = false;
        this.isRecording = false;
        this.isOverlayVisible = false;
        this.currentTab = null;
        this.init();
    }

    async init() {
        // Get current tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        this.currentTab = tab;
        
        // Initialize UI
        this.updateMeetingInfo();
        this.updateStatus();
        this.bindEvents();
        
        // Check connection status
        this.checkConnection();
    }

    updateMeetingInfo() {
        const platform = this.detectPlatform();
        const meetingDetails = document.getElementById('meeting-details');
        const platformSpan = document.getElementById('meeting-platform');
        const statusSpan = document.getElementById('meeting-status');
        
        if (platform) {
            platformSpan.textContent = platform;
            statusSpan.textContent = 'In meeting';
            statusSpan.style.color = '#10b981';
        } else {
            platformSpan.textContent = 'None';
            statusSpan.textContent = 'Not in meeting';
            statusSpan.style.color = '#6b7280';
        }
    }

    detectPlatform() {
        if (!this.currentTab) return null;
        
        const url = this.currentTab.url;
        
        if (url.includes('meet.google.com')) {
            return 'Google Meet';
        } else if (url.includes('teams.microsoft.com')) {
            return 'Microsoft Teams';
        } else if (url.includes('zoom.us')) {
            return 'Zoom';
        }
        
        return null;
    }

    updateStatus() {
        // Connection status
        const connectionStatus = document.getElementById('connection-status');
        const connectionText = document.getElementById('connection-text');
        
        if (this.isConnected) {
            connectionStatus.className = 'status-dot status-online';
            connectionText.textContent = 'Connected';
        } else {
            connectionStatus.className = 'status-dot status-offline';
            connectionText.textContent = 'Disconnected';
        }

        // Recording status
        const recordingStatus = document.getElementById('recording-status');
        const recordingText = document.getElementById('recording-text');
        
        if (this.isRecording) {
            recordingStatus.className = 'status-dot status-error';
            recordingText.textContent = 'Recording';
        } else {
            recordingStatus.className = 'status-dot status-offline';
            recordingText.textContent = 'Stopped';
        }

        // AI status
        const aiStatus = document.getElementById('ai-status');
        const aiText = document.getElementById('ai-text');
        
        if (this.isConnected && this.isRecording) {
            aiStatus.className = 'status-dot status-online';
            aiText.textContent = 'Active';
        } else {
            aiStatus.className = 'status-dot status-offline';
            aiText.textContent = 'Inactive';
        }
    }

    bindEvents() {
        document.getElementById('connect-btn').addEventListener('click', () => {
            this.connect();
        });

        document.getElementById('start-recording-btn').addEventListener('click', () => {
            this.startRecording();
        });

        document.getElementById('stop-recording-btn').addEventListener('click', () => {
            this.stopRecording();
        });

        document.getElementById('toggle-overlay-btn').addEventListener('click', () => {
            this.toggleOverlay();
        });

        document.getElementById('open-settings-btn').addEventListener('click', () => {
            this.openSettings();
        });

        document.getElementById('help-link').addEventListener('click', (e) => {
            e.preventDefault();
            this.openHelp();
        });
    }

    async connect() {
        const connectBtn = document.getElementById('connect-btn');
        const originalText = connectBtn.textContent;
        
        connectBtn.innerHTML = '<div class="loading"></div> Connecting...';
        connectBtn.disabled = true;

        try {
            // Simulate connection to backend
            await this.simulateConnection();
            
            this.isConnected = true;
            this.updateStatus();
            this.updateButtonStates();
            
            connectBtn.textContent = 'Disconnect';
            connectBtn.className = 'control-button btn-danger';
            
            // Inject overlay into current tab
            if (this.detectPlatform()) {
                await this.injectOverlay();
            }
            
        } catch (error) {
            console.error('Connection failed:', error);
            connectBtn.textContent = 'Retry Connection';
            connectBtn.className = 'control-button btn-primary';
        } finally {
            connectBtn.disabled = false;
        }
    }

    async simulateConnection() {
        // Simulate API call to backend
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                // Simulate success/failure
                if (Math.random() > 0.1) { // 90% success rate
                    resolve();
                } else {
                    reject(new Error('Connection failed'));
                }
            }, 2000);
        });
    }

    async startRecording() {
        const startBtn = document.getElementById('start-recording-btn');
        const stopBtn = document.getElementById('stop-recording-btn');
        
        startBtn.disabled = true;
        startBtn.innerHTML = '<div class="loading"></div> Starting...';
        
        try {
            // Send message to content script to start recording
            await chrome.tabs.sendMessage(this.currentTab.id, {
                action: 'startRecording'
            });
            
            this.isRecording = true;
            this.updateStatus();
            this.updateButtonStates();
            
            startBtn.disabled = true;
            stopBtn.disabled = false;
            
        } catch (error) {
            console.error('Failed to start recording:', error);
            startBtn.disabled = false;
            startBtn.textContent = 'Start Recording';
        }
    }

    async stopRecording() {
        const startBtn = document.getElementById('start-recording-btn');
        const stopBtn = document.getElementById('stop-recording-btn');
        
        stopBtn.disabled = true;
        stopBtn.innerHTML = '<div class="loading"></div> Stopping...';
        
        try {
            // Send message to content script to stop recording
            await chrome.tabs.sendMessage(this.currentTab.id, {
                action: 'stopRecording'
            });
            
            this.isRecording = false;
            this.updateStatus();
            this.updateButtonStates();
            
            startBtn.disabled = false;
            stopBtn.disabled = true;
            
        } catch (error) {
            console.error('Failed to stop recording:', error);
            stopBtn.disabled = false;
            stopBtn.textContent = 'Stop Recording';
        }
    }

    async toggleOverlay() {
        const overlayBtn = document.getElementById('toggle-overlay-btn');
        
        try {
            // Send message to content script to toggle overlay
            await chrome.tabs.sendMessage(this.currentTab.id, {
                action: 'toggleOverlay'
            });
            
            this.isOverlayVisible = !this.isOverlayVisible;
            overlayBtn.textContent = this.isOverlayVisible ? 'Hide Overlay' : 'Show Overlay';
            
        } catch (error) {
            console.error('Failed to toggle overlay:', error);
        }
    }

    async injectOverlay() {
        try {
            await chrome.scripting.executeScript({
                target: { tabId: this.currentTab.id },
                files: ['overlay.js']
            });
            
            await chrome.scripting.insertCSS({
                target: { tabId: this.currentTab.id },
                files: ['overlay.css']
            });
            
        } catch (error) {
            console.error('Failed to inject overlay:', error);
        }
    }

    updateButtonStates() {
        const connectBtn = document.getElementById('connect-btn');
        const startRecordingBtn = document.getElementById('start-recording-btn');
        const stopRecordingBtn = document.getElementById('stop-recording-btn');
        const toggleOverlayBtn = document.getElementById('toggle-overlay-btn');
        
        // Enable/disable buttons based on connection status
        if (this.isConnected) {
            connectBtn.textContent = 'Disconnect';
            connectBtn.className = 'control-button btn-danger';
            startRecordingBtn.disabled = false;
            toggleOverlayBtn.disabled = false;
        } else {
            connectBtn.textContent = 'Connect to Service';
            connectBtn.className = 'control-button btn-primary';
            startRecordingBtn.disabled = true;
            stopRecordingBtn.disabled = true;
            toggleOverlayBtn.disabled = true;
        }
        
        // Recording button states
        if (this.isRecording) {
            startRecordingBtn.disabled = true;
            stopRecordingBtn.disabled = false;
        } else {
            startRecordingBtn.disabled = !this.isConnected;
            stopRecordingBtn.disabled = true;
        }
    }

    async checkConnection() {
        // Check if we're connected to the backend service
        try {
            // Simulate health check
            this.isConnected = false; // Will be true when backend is running
            this.updateStatus();
            this.updateButtonStates();
        } catch (error) {
            console.error('Health check failed:', error);
        }
    }

    openSettings() {
        chrome.tabs.create({
            url: chrome.runtime.getURL('settings.html')
        });
    }

    openHelp() {
        chrome.tabs.create({
            url: 'https://github.com/interviewai/assistant#help'
        });
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PopupManager();
});
