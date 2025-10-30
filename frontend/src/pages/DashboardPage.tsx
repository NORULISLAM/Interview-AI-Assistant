import {
  Clock,
  Eye,
  EyeOff,
  FileText,
  Mic,
  MicOff,
  Play,
  Settings,
  Upload,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import LoadingSpinner from "../components/LoadingSpinner";
import { resumeAPI, sessionAPI } from "../lib/api";
import { useAuthStore } from "../stores/authStore";
import { useSessionStore } from "../stores/sessionStore";

const DashboardPage: React.FC = () => {
  const { user, logout } = useAuthStore();
  const {
    isRecording,
    isOverlayVisible,
    startSession,
    stopSession,
    toggleRecording,
    toggleOverlay,
  } = useSessionStore();

  const [sessions, setSessions] = useState<any[]>([]);
  const [resumes, setResumes] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [sessionsResponse, resumesResponse] = await Promise.all([
        sessionAPI.getAll({ limit: 10 }),
        resumeAPI.getAll(),
      ]);

      // setSessions(sessionsResponse.data);
      // setResumes(resumesResponse.data);

      setSessions(sessionsResponse.data.items ?? []);
      setResumes(resumesResponse.data ?? []);
    } catch (error) {
      console.error("Failed to load data:", error);
      toast.error("Failed to load dashboard data");
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartSession = async () => {
    setIsStarting(true);
    try {
      const response = await sessionAPI.create({
        platform: "desktop",
        session_type: "interview",
        // retention_policy: user?.auto_delete_enabled ? "auto" : "manual",
        retention_policy: "auto",
      });

      await startSession(response.data.id);
      toast.success("Interview session started!");
      loadData(); // Refresh sessions
    } catch (error) {
      console.error("Failed to start session:", error);
      toast.error("Failed to start session");
    } finally {
      setIsStarting(false);
    }
  };

  const handleUploadResume = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      toast.error("File size must be less than 10MB");
      return;
    }

    try {
      await resumeAPI.upload(file);
      toast.success("Resume uploaded successfully!");
      loadData(); // Refresh resumes
    } catch (error) {
      console.error("Failed to upload resume:", error);
      toast.error("Failed to upload resume");
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Interview AI Assistant
              </h1>
            </div>

            <div className="flex items-center space-x-4">
              {/* Overlay Toggle */}
              <button
                onClick={toggleOverlay}
                className={`p-2 rounded-lg transition-colors ${
                  isOverlayVisible
                    ? "bg-primary-100 text-primary-600"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
                title="Toggle Overlay"
              >
                {isOverlayVisible ? (
                  <Eye className="h-5 w-5" />
                ) : (
                  <EyeOff className="h-5 w-5" />
                )}
              </button>

              {/* Settings */}
              <button
                onClick={() => (window.location.href = "/settings")}
                className="p-2 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
                title="Settings"
              >
                <Settings className="h-5 w-5" />
              </button>

              {/* User Menu */}
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-700">{user?.email}</span>
                <button
                  onClick={logout}
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  Sign out
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Start Session */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Start Interview
              </h3>
              <Play className="h-6 w-6 text-primary-600" />
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Begin a new interview session with AI assistance
            </p>
            <button
              onClick={handleStartSession}
              disabled={isStarting || isRecording}
              className="w-full btn-primary py-2 px-4 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isStarting ? <LoadingSpinner size="sm" /> : "Start Session"}
            </button>
          </div>

          {/* Upload Resume */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Upload Resume
              </h3>
              <Upload className="h-6 w-6 text-green-600" />
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Upload your resume for personalized suggestions
            </p>
            <label className="w-full btn-secondary py-2 px-4 rounded-md cursor-pointer inline-block text-center">
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={handleUploadResume}
                className="hidden"
              />
              Choose File
            </label>
          </div>

          {/* Recording Status */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Recording</h3>
              {isRecording ? (
                <Mic className="h-6 w-6 text-red-600" />
              ) : (
                <MicOff className="h-6 w-6 text-gray-400" />
              )}
            </div>
            <p className="text-sm text-gray-600 mb-4">
              {isRecording ? "Currently recording audio" : "Not recording"}
            </p>
            <button
              onClick={toggleRecording}
              className={`w-full py-2 px-4 rounded-md ${
                isRecording
                  ? "bg-red-100 text-red-700 hover:bg-red-200"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {isRecording ? "Stop Recording" : "Start Recording"}
            </button>
          </div>
        </div>

        {/* Recent Sessions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Recent Sessions
            </h3>
            {sessions.length > 0 ? (
              <div className="space-y-3">
                {sessions.slice(0, 5).map((session) => (
                  <div
                    key={session.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <Clock className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {session.session_type} - {session.platform}
                        </p>
                        {/* <p className="text-xs text-gray-500">
                          {new Date(session.started_at).toLocaleDateString()}
                        </p> */}
                        <p className="text-xs text-gray-500">
                          Status: {session.status}
                        </p>
                      </div>
                    </div>
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${
                        session.is_active
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {session.is_active ? "Active" : "Ended"}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No sessions yet</p>
            )}
          </div>

          {/* Resumes */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Your Resumes
            </h3>
            {resumes.length > 0 ? (
              <div className="space-y-3">
                {resumes.map((resume) => (
                  <div
                    key={resume.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <FileText className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {resume.filename}
                        </p>
                        {/* <p className="text-xs text-gray-500">
                          {(resume.file_size / 1024 / 1024).toFixed(1)} MB
                        </p> */}

                        <p className="text-xs text-gray-500">Uploaded</p>
                      </div>
                    </div>
                    <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                      Active
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No resumes uploaded</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
