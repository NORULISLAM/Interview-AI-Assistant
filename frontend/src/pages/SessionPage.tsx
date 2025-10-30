import {
  ArrowLeft,
  Mic,
  MicOff,
  Send,
  ThumbsDown,
  ThumbsUp,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { useParams } from "react-router-dom";
import LoadingSpinner from "../components/LoadingSpinner";
import { llmAPI, sessionAPI } from "../lib/api";

type SessionModel = {
  id: number;
  status: "active" | "ended" | string;
  platform?: string;
  session_type?: string;
  started_at?: string; // optional in mock
  ended_at?: string; // optional in mock
  duration_minutes?: number; // optional in mock
  [k: string]: any;
};

type SuggestionModel = {
  id: number;
  text: string; // mock backend field
  accepted?: boolean;
  dismissed?: boolean;
};

const SessionPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [session, setSession] = useState<SessionModel | null>(null);
  const [transcript, setTranscript] = useState<string[]>([]);
  const [suggestions, setSuggestions] = useState<SuggestionModel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  const [chatMessage, setChatMessage] = useState("");

  useEffect(() => {
    if (sessionId) loadSessionData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  const loadSessionData = async () => {
    setIsLoading(true);
    try {
      const id = parseInt(sessionId!, 10);
      const [sessionRes, suggestionsRes] = await Promise.all([
        sessionAPI.getById(id), // -> object
        llmAPI.getSuggestions(id), // -> {items, total}
      ]);

      setSession(sessionRes.data as SessionModel);

      const items = (suggestionsRes.data?.items ?? []) as Array<{
        id: number;
        text: string;
      }>;
      // normalize to UI shape
      setSuggestions(items.map((s) => ({ id: s.id, text: s.text })));
    } catch (e) {
      console.error("Failed to load session data:", e);
      toast.error("Failed to load session data");
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartRecording = () => {
    setIsRecording(true);
    toast.success("Recording started (mock)");
  };

  const handleStopRecording = () => {
    setIsRecording(false);
    toast.success("Recording stopped (mock)");
  };

  const handleSendMessage = async () => {
    if (!chatMessage.trim() || !sessionId) return;
    try {
      const id = parseInt(sessionId, 10);
      const res = await llmAPI.chat(chatMessage, id); // mock returns {reply, session_id}
      const reply = res.data?.reply ?? "(no reply)";
      setTranscript((prev) => [...prev, `You: ${chatMessage}`, `AI: ${reply}`]);
      setChatMessage("");
    } catch (e) {
      console.error("Failed to send message:", e);
      toast.error("Failed to send message");
    }
  };

  const handleSuggestionFeedback = async (
    suggestionId: number,
    accepted: boolean
  ) => {
    try {
      await llmAPI.updateFeedback(suggestionId, {
        accepted,
        rating: accepted ? 5 : 1,
      });
      setSuggestions((prev) =>
        prev.map((s) =>
          s.id === suggestionId ? { ...s, accepted, dismissed: !accepted } : s
        )
      );
      toast.success(accepted ? "Suggestion accepted" : "Suggestion dismissed");
    } catch (e) {
      console.error("Failed to update feedback:", e);
      toast.error("Failed to update feedback");
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Session not found
          </h2>
          <button
            onClick={() => (window.location.href = "/")}
            className="btn-primary"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const isActive = (session.status ?? "").toLowerCase() === "active";

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16">
            <button
              onClick={() => (window.location.href = "/")}
              className="mr-4 p-2 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div className="flex-1">
              <h1 className="text-xl font-semibold text-gray-900">
                Interview Session
                {session.session_type ? ` - ${session.session_type}` : ""}
              </h1>
              <p className="text-sm text-gray-500">
                {session.started_at
                  ? `Started ${new Date(session.started_at).toLocaleString()}`
                  : "Started: N/A"}
              </p>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={
                  isRecording ? handleStopRecording : handleStartRecording
                }
                className={`p-3 rounded-full transition-colors ${
                  isRecording
                    ? "bg-red-100 text-red-600 hover:bg-red-200"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {isRecording ? (
                  <MicOff className="h-5 w-5" />
                ) : (
                  <Mic className="h-5 w-5" />
                )}
              </button>

              <span
                className={`px-3 py-1 text-sm rounded-full ${
                  isActive
                    ? "bg-green-100 text-green-800"
                    : "bg-gray-100 text-gray-800"
                }`}
              >
                {isActive ? "Active" : "Ended"}
              </span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Transcript */}
          <div className="lg:col-span-2 space-y-6">
            <div className="card p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Live Transcript
              </h3>

              {transcript.length > 0 ? (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {transcript.map((line, index) => (
                    <div key={index} className="p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-800">{line}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Mic className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>Start recording to see the transcript here</p>
                </div>
              )}
            </div>

            {/* Chat */}
            <div className="card p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Chat with AI
              </h3>

              <div className="flex space-x-2">
                <input
                  type="text"
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                  placeholder="Ask a question or request help..."
                  className="flex-1 input"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!chatMessage.trim()}
                  className="btn-primary px-4"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Suggestions */}
          <div className="space-y-6">
            <div className="card p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                AI Suggestions
              </h3>

              {suggestions.length > 0 ? (
                <div className="space-y-3">
                  {suggestions.map((s) => (
                    <div
                      key={s.id}
                      className="p-4 bg-blue-50 border border-blue-200 rounded-lg"
                    >
                      <div className="mb-3">
                        <span className="inline-block px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full mb-2">
                          TIP
                        </span>
                        <p className="text-sm text-gray-800">{s.text}</p>
                      </div>

                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleSuggestionFeedback(s.id, true)}
                          className={`flex-1 py-1 px-3 text-xs rounded ${
                            s.accepted
                              ? "bg-green-100 text-green-700"
                              : "bg-gray-100 text-gray-700 hover:bg-green-100 hover:text-green-700"
                          }`}
                        >
                          <ThumbsUp className="h-3 w-3 inline mr-1" />
                          Useful
                        </button>
                        <button
                          onClick={() => handleSuggestionFeedback(s.id, false)}
                          className={`flex-1 py-1 px-3 text-xs rounded ${
                            s.dismissed
                              ? "bg-red-100 text-red-700"
                              : "bg-gray-100 text-gray-700 hover:bg-red-100 hover:text-red-700"
                          }`}
                        >
                          <ThumbsDown className="h-3 w-3 inline mr-1" />
                          Not useful
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>AI suggestions will appear here during your interview</p>
                </div>
              )}
            </div>

            {/* Session Info */}
            <div className="card p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Session Info
              </h3>
              <div className="space-y-3">
                <div>
                  <span className="text-sm font-medium text-gray-700">
                    Platform:
                  </span>
                  <span className="ml-2 text-sm text-gray-600">
                    {session.platform ?? "N/A"}
                  </span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-700">
                    Type:
                  </span>
                  <span className="ml-2 text-sm text-gray-600">
                    {session.session_type ?? "N/A"}
                  </span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-700">
                    Status:
                  </span>
                  <span className="ml-2 text-sm text-gray-600">
                    {session.status}
                  </span>
                </div>
                {session.started_at && (
                  <div>
                    <span className="text-sm font-medium text-gray-700">
                      Started:
                    </span>
                    <span className="ml-2 text-sm text-gray-600">
                      {new Date(session.started_at).toLocaleString()}
                    </span>
                  </div>
                )}
                {session.ended_at && (
                  <div>
                    <span className="text-sm font-medium text-gray-700">
                      Ended:
                    </span>
                    <span className="ml-2 text-sm text-gray-600">
                      {new Date(session.ended_at).toLocaleString()}
                    </span>
                  </div>
                )}
                {typeof session.duration_minutes === "number" && (
                  <div>
                    <span className="text-sm font-medium text-gray-700">
                      Duration:
                    </span>
                    <span className="ml-2 text-sm text-gray-600">
                      {session.duration_minutes} minutes
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SessionPage;
