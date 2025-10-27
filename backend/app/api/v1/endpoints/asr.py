"""
ASR (Speech Recognition) endpoints
"""
import json
import asyncio
from typing import Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import StreamingResponse
import httpx
import io

from app.core.config import settings
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

# ASR service URL
ASR_SERVICE_URL = "http://localhost:8001"


@router.websocket("/ws/{session_id}")
async def websocket_asr(
    websocket: WebSocket,
    session_id: int,
    current_user: User = Depends(get_current_user)
):
    """WebSocket endpoint for real-time ASR"""
    await websocket.accept()
    
    try:
        # Connect to ASR service
        async with httpx.AsyncClient() as client:
            async with client.websocket_connect(f"{ASR_SERVICE_URL}/ws/transcribe") as asr_ws:
                
                # Start bidirectional forwarding
                async def forward_to_asr():
                    try:
                        while True:
                            data = await websocket.receive_bytes()
                            await asr_ws.send_bytes(data)
                    except WebSocketDisconnect:
                        pass
                
                async def forward_from_asr():
                    try:
                        while True:
                            data = await asr_ws.receive_text()
                            
                            # Add session context to the response
                            result = json.loads(data)
                            result["session_id"] = session_id
                            result["user_id"] = current_user.id
                            
                            await websocket.send_text(json.dumps(result))
                    except Exception:
                        pass
                
                # Run both forwarding tasks concurrently
                await asyncio.gather(
                    forward_to_asr(),
                    forward_from_asr(),
                    return_exceptions=True
                )
                
    except Exception as e:
        print(f"ASR WebSocket error: {e}")
    finally:
        await websocket.close()


@router.post("/transcribe/{session_id}")
async def transcribe_audio(
    session_id: int,
    audio_data: bytes,
    current_user: User = Depends(get_current_user)
):
    """HTTP endpoint for one-shot transcription"""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ASR_SERVICE_URL}/transcribe",
                content=audio_data,
                headers={"Content-Type": "application/octet-stream"}
            )
            response.raise_for_status()
            
            result = response.json()
            result["session_id"] = session_id
            result["user_id"] = current_user.id
            
            return result
            
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"ASR service error: {str(e)}")


@router.get("/health")
async def asr_health_check():
    """Check ASR service health"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ASR_SERVICE_URL}/health")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        return {
            "status": "unhealthy",
            "asr_service": "down"
        }
