import { Toaster } from "react-hot-toast";
import { Route, Routes } from "react-router-dom";

// Pages
import DashboardPage from "./pages/DashboardPage";
import SessionPage from "./pages/SessionPage";
import SettingsPage from "./pages/SettingsPage";

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        {/* Direct access to all pages - no authentication needed */}
        <Route path="/" element={<DashboardPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/session/:sessionId" element={<SessionPage />} />
      </Routes>

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: "#363636",
            color: "#fff",
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: "#10B981",
              secondary: "#fff",
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: "#EF4444",
              secondary: "#fff",
            },
          },
        }}
      />
    </div>
  );
}

export default App;
