import {
  app,
  BrowserWindow,
  globalShortcut,
  ipcMain,
  Menu,
  screen,
} from "electron";
import isDev from "electron-is-dev";
import path from "path";

let mainWindow: BrowserWindow | null = null;
let overlayWindow: BrowserWindow | null = null;

const createMainWindow = () => {
  // Create the main application window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
      webSecurity: !isDev,
    },
    titleBarStyle: "default",
    show: false,
    icon: path.join(__dirname, "../assets/icon.png"),
  });

  // Load the app
  const startUrl = isDev
    ? "http://localhost:5173"
    : `file://${path.join(__dirname, "../dist/index.html")}`;

  mainWindow.loadURL(startUrl);

  // Show window when ready
  mainWindow.once("ready-to-show", () => {
    mainWindow?.show();

    if (isDev) {
      mainWindow?.webContents.openDevTools();
    }
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
};

const createOverlayWindow = () => {
  if (overlayWindow) {
    return overlayWindow;
  }

  // Get primary display
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  // Create overlay window
  overlayWindow = new BrowserWindow({
    width: 400,
    height: 300,
    x: width - 420,
    y: height - 320,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
      webSecurity: false, // Allow overlay functionality
    },
    frame: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    minimizable: false,
    maximizable: false,
    closable: false,
    show: false,
    transparent: true,
    backgroundColor: "#00000000",
  });

  // Load overlay content
  overlayWindow.loadFile(path.join(__dirname, "../overlay/index.html"));

  overlayWindow.on("closed", () => {
    overlayWindow = null;
  });

  // Make window click-through when not focused
  overlayWindow.setIgnoreMouseEvents(true, { forward: true });

  return overlayWindow;
};

// App event handlers
app.whenReady().then(() => {
  createMainWindow();
  createOverlayWindow();

  // Register global shortcuts
  globalShortcut.register("CommandOrControl+Shift+I", () => {
    if (overlayWindow) {
      overlayWindow.isVisible() ? overlayWindow.hide() : overlayWindow.show();
    }
  });

  globalShortcut.register("CommandOrControl+Shift+M", () => {
    if (mainWindow) {
      mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
    }
  });

  // Create application menu
  const template = [
    {
      label: "Interview AI",
      submenu: [
        {
          label: "Show Main Window",
          accelerator: "CmdOrCtrl+Shift+M",
          click: () => mainWindow?.show(),
        },
        {
          label: "Toggle Overlay",
          accelerator: "CmdOrCtrl+Shift+I",
          click: () => {
            if (overlayWindow) {
              overlayWindow.isVisible()
                ? overlayWindow.hide()
                : overlayWindow.show();
            }
          },
        },
        { type: "separator" },
        {
          label: "Quit",
          accelerator: process.platform === "darwin" ? "Cmd+Q" : "Ctrl+Q",
          click: () => app.quit(),
        },
      ],
    },
    {
      label: "View",
      submenu: [
        { role: "reload" },
        { role: "forceReload" },
        { role: "toggleDevTools" },
        { type: "separator" },
        { role: "resetZoom" },
        { role: "zoomIn" },
        { role: "zoomOut" },
        { type: "separator" },
        { role: "togglefullscreen" },
      ],
    },
  ];

  const menu = Menu.buildFromTemplate(template as any);
  Menu.setApplicationMenu(menu);
});

app.on("window-all-closed", () => {
  // On macOS, keep app running even when all windows are closed
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  // On macOS, re-create window when dock icon is clicked
  if (BrowserWindow.getAllWindows().length === 0) {
    createMainWindow();
  }
});

app.on("will-quit", () => {
  // Unregister all shortcuts
  globalShortcut.unregisterAll();
});

// IPC handlers
ipcMain.handle("get-app-version", () => {
  return app.getVersion();
});

ipcMain.handle("show-overlay", () => {
  if (overlayWindow) {
    overlayWindow.show();
    overlayWindow.focus();
  }
});

ipcMain.handle("hide-overlay", () => {
  if (overlayWindow) {
    overlayWindow.hide();
  }
});

ipcMain.handle("toggle-overlay", () => {
  if (overlayWindow) {
    overlayWindow.isVisible() ? overlayWindow.hide() : overlayWindow.show();
  }
});

ipcMain.handle("set-overlay-position", (event, x, y) => {
  if (overlayWindow) {
    overlayWindow.setPosition(x, y);
  }
});

ipcMain.handle("get-screen-size", () => {
  const primaryDisplay = screen.getPrimaryDisplay();
  return {
    width: primaryDisplay.workAreaSize.width,
    height: primaryDisplay.workAreaSize.height,
  };
});

// Audio recording handlers
ipcMain.handle("start-recording", async () => {
  // TODO: Implement audio recording
  console.log("Starting audio recording...");
  return { success: true };
});

ipcMain.handle("stop-recording", async () => {
  // TODO: Implement stop recording
  console.log("Stopping audio recording...");
  return { success: true };
});

ipcMain.handle("get-audio-devices", async () => {
  // TODO: Get available audio devices
  return [];
});
