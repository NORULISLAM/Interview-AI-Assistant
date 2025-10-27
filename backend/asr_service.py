"""
Standalone ASR service using Faster-Whisper
"""
import asyncio
import json
import logging
from typing import Dict, Any
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from faster_whisper import WhisperModel
import numpy as np
import io
import wave

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instance
whisper_model = None

app = FastAPI(title="ASR Service", version="1.0.0")


@app.on_event("startup")
async def startup_event():
    """Initialize Whisper model on startup"""
    global whisper_model
    try:
        logger.info(f"Loading Whisper model: {settings.ASR_MODEL}")
        whisper_model = WhisperModel(
            settings.ASR_MODEL,
            device=settings.ASR_DEVICE,
            compute_type="float16" if settings.ASR_DEVICE == "cuda" else "int8"
        )
        logger.info("Whisper model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load Whisper model: {e}")
        raise


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": whisper_model is not None,
        "model": settings.ASR_MODEL,
        "device": settings.ASR_DEVICE
    }


@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """WebSocket endpoint for real-time transcription"""
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()
            
            if not data:
                continue
            
            # Decode audio
            audio_array = decode_audio_data(data)
            
            if audio_array is None or len(audio_array) == 0:
                continue
            
            # Transcribe audio
            try:
                segments, info = whisper_model.transcribe(
                    audio_array,
                    beam_size=1,  # Faster inference
                    language="en",
                    condition_on_previous_text=False,
                    temperature=0.0
                )
                
                # Send partial results
                for segment in segments:
                    result = {
                        "type": "partial",
                        "text": segment.text.strip(),
                        "start": segment.start,
                        "end": segment.end,
                        "confidence": getattr(segment, 'avg_logprob', 0.0)
                    }
                    await websocket.send_text(json.dumps(result))
                
                # Send final result
                full_text = " ".join([segment.text.strip() for segment in segments])
                if full_text:
                    result = {
                        "type": "final",
                        "text": full_text,
                        "start": info.duration if hasattr(info, 'duration') else 0,
                        "end": info.duration if hasattr(info, 'duration') else 0,
                        "confidence": 0.8  # Default confidence
                    }
                    await websocket.send_text(json.dumps(result))
                    
            except Exception as e:
                logger.error(f"Transcription error: {e}")
                error_result = {
                    "type": "error",
                    "message": str(e)
                }
                await websocket.send_text(json.dumps(error_result))
                
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


def decode_audio_data(data: bytes) -> np.ndarray:
    """Decode audio data to numpy array"""
    try:
        # Try to decode as WAV
        audio_io = io.BytesIO(data)
        with wave.open(audio_io, 'rb') as wav_file:
            frames = wav_file.readframes(-1)
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            
            # Convert to numpy array
            if sample_width == 1:
                dtype = np.uint8
            elif sample_width == 2:
                dtype = np.int16
            elif sample_width == 4:
                dtype = np.int32
            else:
                logger.error(f"Unsupported sample width: {sample_width}")
                return None
            
            audio_array = np.frombuffer(frames, dtype=dtype)
            
            # Convert to mono if stereo
            if channels == 2:
                audio_array = audio_array.reshape(-1, 2).mean(axis=1)
            
            # Normalize to float32
            if dtype == np.uint8:
                audio_array = (audio_array - 128) / 128.0
            elif dtype == np.int16:
                audio_array = audio_array / 32768.0
            elif dtype == np.int32:
                audio_array = audio_array / 2147483648.0
            
            return audio_array.astype(np.float32)
            
    except Exception as e:
        logger.error(f"Failed to decode audio data: {e}")
        return None


@app.post("/transcribe")
async def transcribe_audio(audio_data: bytes):
    """HTTP endpoint for one-shot transcription"""
    if whisper_model is None:
        raise HTTPException(status_code=503, detail="ASR service not ready")
    
    audio_array = decode_audio_data(audio_data)
    
    if audio_array is None:
        raise HTTPException(status_code=400, detail="Invalid audio data")
    
    try:
        segments, info = whisper_model.transcribe(
            audio_array,
            beam_size=1,
            language="en"
        )
        
        result = {
            "text": " ".join([segment.text.strip() for segment in segments]),
            "segments": [
                {
                    "text": segment.text.strip(),
                    "start": segment.start,
                    "end": segment.end
                }
                for segment in segments
            ],
            "language": info.language if hasattr(info, 'language') else "en",
            "duration": info.duration if hasattr(info, 'duration') else 0
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "asr_service:app",
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
