## file test:

curl.exe -X POST "http://127.0.0.1:8000/api/v1/resumes/" `
-F "file=@C:\Users\n-islam\Downloads\resume.pdf"
List all resumes

Invoke-RestMethod http://127.0.0.1:8000/api/v1/resumes/ -Method GET

Get one resume (use the id you saw, e.g., 1)

Invoke-RestMethod http://127.0.0.1:8000/api/v1/resumes/1 -Method GET

Delete it

Invoke-RestMethod http://127.0.0.1:8000/api/v1/resumes/1 -Method DELETE

Health + mock auth + mock ASR

Invoke-RestMethod http://127.0.0.1:8000/api/v1/health -Method GET
Invoke-RestMethod http://127.0.0.1:8000/api/v1/auth/me -Method GET

# send any bytes to ASR mock

curl.exe -X POST "http://127.0.0.1:8000/api/v1/asr/transcribe/123" --data-binary "hello" -H "Content-Type: application/octet-stream"

Open API docs (try endpoints in browser)

http://127.0.0.1:8000/docs

6. Quick manual tests (browser)

Open http://localhost:5173.

Click Start Session → “Interview session started!”; “Recent Sessions” shows an item (status).

Upload Resume → toast success; “Your Resumes” shows the file name.

If something fails, open DevTools → Network:

Requests should be http://localhost:5173/api/v1/... (proxied).

Responses: sessions ⇒ {items:[...]}, resumes ⇒ [{id,filename}].

## FULL APPLICATION OVERVIEWS :　

Got it. Here’s the “wiring map” of your app—**which frontend code calls which backend route** and where to change things.

# Core connection

- **Vite proxy** → `vite.config.ts`

  - `"/api" → http://localhost:8000` (so FE calls `/api/v1/...` and it hits FastAPI)

- **HTTP client** → `src/lib/api.ts`

  - Base URL:

    - Dev: `"/api/v1"`
    - Prod: `import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1"`

---

# Endpoints map (Frontend ↔ Backend)

## Health / ASR

- FE: `asrAPI.getHealth()` in `src/lib/api.ts`

  - Calls: `GET /api/v1/asr/health`

- BE: `@app.get("/api/v1/asr/health")` in `main.py`

## Auth (mock, no real login)

- FE: `authAPI.getMe()` in `src/lib/api.ts`

  - Calls: `GET /api/v1/auth/me`

- BE: `@app.get("/api/v1/auth/me")` in `main.py`
  (remove bearer check if testing without auth)

_(You also have magic-link endpoints wired in `api.ts`, but your UI currently doesn’t use them.)_

## User settings (SettingsPage)

- FE file: `src/pages/SettingsPage.tsx`

  - Load/Save:

    - `userAPI.getProfile()` → `GET /users/me`
    - `userAPI.updateProfile(data)` → `PATCH /users/me`
    - `userAPI.deleteAccount()` → `DELETE /users/me`

- BE: add these mock handlers to `main.py`:

  - `@app.get("/api/v1/users/me")`
  - `@app.patch("/api/v1/users/me")`
  - `@app.delete("/api/v1/users/me")`

## Sessions (Dashboard & Session pages)

- FE files:

  - `src/pages/DashboardPage.tsx`

    - `sessionAPI.getAll({limit})` → `GET /sessions/`
    - `sessionAPI.create(payload)` → `POST /sessions/`

  - `src/pages/SessionPage.tsx`

    - `sessionAPI.getById(id)` → `GET /sessions/{id}`
    - `sessionAPI.end(id)` → `PATCH /sessions/{id}/end`
    - `sessionAPI.delete(id)` → `DELETE /sessions/{id}`

- BE (main.py stubs you already have):

  - `@app.post("/api/v1/sessions/")`
  - `@app.get("/api/v1/sessions/")`
  - `@app.get("/api/v1/sessions/{sid}")`
  - `@app.patch("/api/v1/sessions/{sid}/end")`
  - `@app.delete("/api/v1/sessions/{sid}")`

## Resumes (Dashboard upload)

- FE file: `src/pages/DashboardPage.tsx`

  - `resumeAPI.getAll()` → `GET /resumes/`
  - `resumeAPI.upload(file)` → `POST /resumes/` (multipart)
  - `resumeAPI.getById(id)` → `GET /resumes/{id}`
  - `resumeAPI.delete(id)` → `DELETE /resumes/{id}`

- BE (main.py stubs you already have):

  - `@app.post("/api/v1/resumes/")`
  - `@app.get("/api/v1/resumes/")`
  - `@app.get("/api/v1/resumes/{rid}")`
  - `@app.delete("/api/v1/resumes/{rid}")`

## LLM (SessionPage chat + tips)

- FE file: `src/pages/SessionPage.tsx`

  - Suggestions list:
    `llmAPI.getSuggestions(sessionId)` → `GET /llm/suggestions/{session_id}`
    _(UI expects `{items:[{id,text}]}`; you already normalized it in the fixed page)_
  - Feedback:
    `llmAPI.updateFeedback(id, data)` → `PATCH /llm/suggestions/{suggestion_id}/feedback`
  - Chat:
    `llmAPI.chat(message, sessionId)` → `POST /llm/chat`
    _(UI reads `res.data.reply` from backend mock)_

- BE (main.py stubs you already have):

  - `@app.get("/api/v1/llm/suggestions/{session_id}")`
  - `@app.patch("/api/v1/llm/suggestions/{suggestion_id}/feedback")`
  - `@app.post("/api/v1/llm/chat")`

---

# Where UI triggers calls

- **DashboardPage.tsx**

  - `handleStartSession` → `sessionAPI.create` → backend `/sessions/`
  - `handleUploadResume` → `resumeAPI.upload` → backend `/resumes/`
  - `useEffect(loadData)` → `sessionAPI.getAll` + `resumeAPI.getAll`

- **SessionPage.tsx**

  - `useEffect(loadSessionData)` → `sessionAPI.getById` + `llmAPI.getSuggestions`
  - `handleSendMessage` → `llmAPI.chat`
  - `handleSuggestionFeedback` → `llmAPI.updateFeedback`

- **SettingsPage.tsx**

  - `handleSave` → `userAPI.updateProfile`
  - `handleDeleteAccount` → `userAPI.deleteAccount`
  - (Optionally load profile on mount) → `userAPI.getProfile`

---

# Glue you must keep

- **CORS** in `main.py`:

  ```py
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

- **Vite proxy** in `vite.config.ts`:

  ```ts
  proxy: { "/api": { target: "http://localhost:8000", changeOrigin: true, secure: false } }
  ```

---

# Quick test flow (end-to-end)

1. **Backend**

   ```powershell
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **Frontend**

   ```powershell
   npm run dev
   ```

3. In UI:

   - Dashboard → **Start Session** → should create and list a session.
   - **Choose File** → upload → should appear under “Your Resumes”.
   - Open a session → Chat → replies from `/llm/chat`.
   - Settings → change values → **Save Settings** → persists via `/users/me`.

This is the full connection map. If any call 404s, check the matching route in `main.py` against the **exact path** your `api.ts` uses.

###
