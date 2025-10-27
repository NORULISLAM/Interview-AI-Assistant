import { AlertTriangle, ArrowLeft, Save, Trash2 } from "lucide-react";
import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import LoadingSpinner from "../components/LoadingSpinner";
import { userAPI } from "../lib/api";
import { useAuthStore } from "../stores/authStore";

const SettingsPage: React.FC = () => {
  const { user, logout } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [settings, setSettings] = useState({
    auto_delete_enabled: true,
    retention_hours: 24,
    preferred_llm_model: "gpt-4o-mini",
    overlay_position: "bottom-right",
  });

  useEffect(() => {
    if (user) {
      setSettings({
        auto_delete_enabled: user.auto_delete_enabled,
        retention_hours: user.retention_hours,
        preferred_llm_model: user.preferred_llm_model || "gpt-4o-mini",
        overlay_position: user.overlay_position || "bottom-right",
      });
    }
  }, [user]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await userAPI.updateProfile(settings);
      toast.success("Settings saved successfully!");
    } catch (error) {
      console.error("Failed to save settings:", error);
      toast.error("Failed to save settings");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (
      !confirm(
        "Are you sure you want to delete your account? This action cannot be undone."
      )
    ) {
      return;
    }

    if (
      !confirm(
        "This will permanently delete all your data including sessions, transcripts, and resumes. Are you absolutely sure?"
      )
    ) {
      return;
    }

    setIsLoading(true);
    try {
      await userAPI.deleteAccount();
      toast.success("Account deleted successfully");
      logout();
    } catch (error) {
      console.error("Failed to delete account:", error);
      toast.error("Failed to delete account");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16">
            <button
              onClick={() => (window.location.href = "/")}
              className="mr-4 p-2 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <h1 className="text-xl font-semibold text-gray-900">Settings</h1>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Privacy Settings */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Privacy Settings
            </h3>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Auto-delete transcripts
                  </label>
                  <p className="text-sm text-gray-500">
                    Automatically delete transcripts after the specified time
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.auto_delete_enabled}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        auto_delete_enabled: e.target.checked,
                      })
                    }
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>

              {settings.auto_delete_enabled && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Retention period
                  </label>
                  <select
                    value={settings.retention_hours}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        retention_hours: parseInt(e.target.value),
                      })
                    }
                    className="input w-48"
                  >
                    <option value={1}>1 hour</option>
                    <option value={6}>6 hours</option>
                    <option value={24}>24 hours</option>
                    <option value={72}>3 days</option>
                    <option value={168}>1 week</option>
                  </select>
                </div>
              )}
            </div>
          </div>

          {/* AI Settings */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              AI Settings
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Preferred LLM Model
                </label>
                <select
                  value={settings.preferred_llm_model}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      preferred_llm_model: e.target.value,
                    })
                  }
                  className="input w-64"
                >
                  <option value="gpt-4o-mini">
                    GPT-4o Mini (Fast, Cost-effective)
                  </option>
                  <option value="gpt-4o">GPT-4o (High Quality)</option>
                  <option value="claude-3-5-sonnet">
                    Claude 3.5 Sonnet (Balanced)
                  </option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Overlay Position
                </label>
                <select
                  value={settings.overlay_position}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      overlay_position: e.target.value,
                    })
                  }
                  className="input w-48"
                >
                  <option value="bottom-right">Bottom Right</option>
                  <option value="bottom-left">Bottom Left</option>
                  <option value="top-right">Top Right</option>
                  <option value="top-left">Top Left</option>
                </select>
              </div>
            </div>
          </div>

          {/* Account Settings */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Account</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={user?.email || ""}
                  disabled
                  className="input w-64 bg-gray-50"
                />
                <p className="text-sm text-gray-500 mt-1">
                  Email cannot be changed
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Member since
                </label>
                <p className="text-sm text-gray-600">
                  {user?.created_at
                    ? new Date(user.created_at).toLocaleDateString()
                    : "Unknown"}
                </p>
              </div>
            </div>
          </div>

          {/* Danger Zone */}
          <div className="card p-6 border-red-200 bg-red-50">
            <h3 className="text-lg font-medium text-red-900 mb-4 flex items-center">
              <AlertTriangle className="h-5 w-5 mr-2" />
              Danger Zone
            </h3>

            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-red-800 mb-2">
                  Delete Account
                </h4>
                <p className="text-sm text-red-700 mb-4">
                  Permanently delete your account and all associated data. This
                  action cannot be undone.
                </p>
                <button
                  onClick={handleDeleteAccount}
                  disabled={isLoading}
                  className="btn bg-red-600 text-white hover:bg-red-700 disabled:opacity-50"
                >
                  {isLoading ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    <>
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete Account
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="btn-primary px-6 py-2"
            >
              {isSaving ? (
                <LoadingSpinner size="sm" />
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Settings
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
